#!/usr/bin/env python3

import base64
import os
import threading
import time

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from openai import APIError, OpenAI
from sensor_msgs.msg import Image
from std_msgs.msg import Empty, String

from detector import DEFAULT_DATA, DEFAULT_WEIGHTS, Detector


TARGETS = {"scissors", "earbuds"}
UNSAFE_CONTEXT_TERMS = (
    "person",
    "people",
    "man",
    "woman",
    "wear",
    "shirt",
    "clothing",
    "identity",
    "violation",
    "illegal",
    "prohibited",
    "forbidden",
    "not allowed",
)


class SafeZoneAssistant:
    def __init__(self):
        rospy.init_node("safezone_assistant")

        self.camera_topic = rospy.get_param(
            "~camera_topic", "/camera/color/image_raw"
        )
        self.window_seconds = float(rospy.get_param("~window_seconds", 10.0))
        self.processing_interval = float(
            rospy.get_param("~processing_interval", 0.35)
        )
        if self.window_seconds <= 0 or self.processing_interval <= 0:
            raise ValueError("window_seconds and processing_interval must be positive")

        self.bridge = CvBridge()
        self.detector = Detector(
            weights=rospy.get_param("~weights", str(DEFAULT_WEIGHTS)),
            data=rospy.get_param("~data", str(DEFAULT_DATA)),
            conf_thres=float(rospy.get_param("~confidence", 0.25)),
            classes=[0, 1],
            view_img=False,
        )
        names = self.detector.names
        model_labels = {
            str(name).strip().lower()
            for name in (names.values() if isinstance(names, dict) else names)
        }
        if not TARGETS.issubset(model_labels):
            raise RuntimeError(
                "SafeZone requires the checkpoint classes scissors and earbuds; "
                f"found {sorted(model_labels)}"
            )

        # Previous key variable: EKD_DASHSCOPE_API_KEY
        api_key = os.environ.get("EKD_QWEN_API_KEY")
        self.client = (
            OpenAI(
                api_key=api_key,
                # Previous endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1
                base_url="https://llm-orqx90gtcezlx878.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
                timeout=20.0,
                max_retries=0,
            )
            if api_key
            else None
        )
        if self.client is None:
            rospy.logwarn(
                "EKD_QWEN_API_KEY is unset; detections will use the "
                "built-in safety message without Qwen context"
            )

        # Previous model: qwen-omni-turbo
        self.model = rospy.get_param("~qwen_model", "qwen3.8-max")
        self.wake_subscriber = rospy.Subscriber(
            "/safezone/wake", Empty, self._on_wake, queue_size=1
        )
        self.speech_publisher = rospy.Publisher(
            "/voiceWords", String, queue_size=1
        )
        self.response_publisher = rospy.Publisher(
            "/safezone/response", String, queue_size=1
        )

        self.lock = threading.Lock()
        self.active = False
        self.processing = False
        self.last_inference = 0.0
        self.image_subscriber = None
        self.window_timer = None
        rospy.on_shutdown(self._shutdown)

    def _on_wake(self, _message):
        with self.lock:
            if self.active or self.processing:
                rospy.loginfo("Ignoring wake phrase while a SafeZone session is busy")
                return
            self.active = True
            self.last_inference = 0.0
            self.image_subscriber = rospy.Subscriber(
                self.camera_topic,
                Image,
                self._on_image,
                queue_size=1,
                buff_size=10 * 1024 * 1024,
            )
            self.window_timer = rospy.Timer(
                rospy.Duration(self.window_seconds), self._on_timeout, oneshot=True
            )

        rospy.loginfo(
            "SafeZone camera monitoring active for %.1f seconds",
            self.window_seconds,
        )

    def _on_timeout(self, _event):
        with self.lock:
            if not self.active:
                return
            self.active = False
            self.image_subscriber.unregister()
            self.image_subscriber = None
            self.window_timer = None
        rospy.loginfo("SafeZone monitoring window ended without a target detection")

    def _on_image(self, message):
        now = time.monotonic()
        with self.lock:
            if not self.active or now - self.last_inference < self.processing_interval:
                return
            self.last_inference = now

        try:
            frame = self.bridge.imgmsg_to_cv2(message, "bgr8")
        except CvBridgeError as error:
            rospy.logwarn("Could not decode camera frame: %s", error)
            return

        try:
            _annotated, detections = self.detector.detect(frame.copy())
        except (RuntimeError, cv2.error) as error:
            rospy.logerr("SafeZone detector failed: %s", error)
            return

        targets = {}
        for detection in detections:
            label = str(detection.name).strip().lower()
            if label in TARGETS:
                targets[label] = max(
                    targets.get(label, 0.0), float(detection.conf)
                )
        if not targets:
            return

        with self.lock:
            if not self.active:
                return
            self.active = False
            self.processing = True
            self.image_subscriber.unregister()
            self.image_subscriber = None
            if self.window_timer is not None:
                self.window_timer.shutdown()
                self.window_timer = None

        rospy.loginfo(
            "SafeZone target detected: %s",
            ", ".join(f"{name} ({score:.2f})" for name, score in targets.items()),
        )
        worker = threading.Thread(
            target=self._analyze_and_speak,
            args=(frame.copy(), targets),
            name="safezone-qwen-event",
            daemon=True,
        )
        worker.start()

    def _analyze_and_speak(self, frame, targets):
        context = ""
        if self.client is not None:
            try:
                context = self._get_visual_context(frame, targets)
            except APIError as error:
                rospy.logerr("Qwen event analysis failed: %s", error)
            except (ValueError, cv2.error) as error:
                rospy.logerr("Could not prepare the SafeZone event image: %s", error)

        message = self._safety_message(targets)
        if context:
            message = f"{message} Visual context: {context}"
        self.response_publisher.publish(String(data=message))
        self.speech_publisher.publish(String(data=message))
        rospy.loginfo("SafeZone spoken response: %s", message)

        with self.lock:
            self.processing = False

    def _get_visual_context(self, frame, targets):
        encoded_ok, encoded_image = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        )
        if not encoded_ok:
            raise ValueError("OpenCV could not encode the captured event frame")

        image_data = base64.b64encode(encoded_image.tobytes()).decode("ascii")
        target_summary = ", ".join(
            f"{name} (YOLO confidence {score:.2f})"
            for name, score in targets.items()
        )
        prompt = (
            "This is one event-triggered still image from a safety-assistant demo. "
            f"The local detector reported: {target_summary}. "
            "Return only a short, neutral phrase (at most 12 words) describing "
            "where the detected object appears in the scene. Do not describe or "
            "identify people, clothing, use, intent, or policy compliance. Do not "
            "claim anyone is wearing earbuds. If the location is unclear, reply "
            "exactly: position unclear."
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        content = response.choices[0].message.content
        if not isinstance(content, str):
            rospy.logwarn("Qwen returned no plain-text visual context")
            return ""

        context = " ".join(content.split()).strip(" .")
        if not context or len(context) > 120:
            rospy.logwarn("Ignoring empty or overly long Qwen visual context")
            return ""
        lowered = context.lower()
        if any(term in lowered for term in UNSAFE_CONTEXT_TERMS):
            rospy.logwarn("Ignoring Qwen context that exceeded the safety prompt")
            return ""
        return context

    @staticmethod
    def _safety_message(targets):
        if targets == {"scissors"}:
            return (
                "SafeZone detected possible scissors in view. Please handle and "
                "store them according to local safety rules."
            )
        if targets == {"earbuds"}:
            return (
                "SafeZone detected possible earbuds in view. This does not confirm "
                "anyone is wearing them; please follow local rules."
            )
        return (
            "SafeZone detected possible scissors and earbuds in view. Please check "
            "the situation and follow local safety rules. Detection does not "
            "confirm anyone is wearing the earbuds."
        )

    def _shutdown(self):
        with self.lock:
            self.active = False
            if self.image_subscriber is not None:
                self.image_subscriber.unregister()
                self.image_subscriber = None
            if self.window_timer is not None:
                self.window_timer.shutdown()
                self.window_timer = None


if __name__ == "__main__":
    SafeZoneAssistant()
    rospy.spin()
