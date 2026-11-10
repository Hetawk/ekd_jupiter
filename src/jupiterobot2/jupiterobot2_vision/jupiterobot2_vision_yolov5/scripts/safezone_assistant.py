#!/usr/bin/env python3

import base64
from datetime import datetime
import json
import os
from pathlib import Path
import re
import rospkg
import sys
import threading
import time
import uuid

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from openai import APIError, OpenAI
from sensor_msgs.msg import Image
from std_msgs.msg import String

package_path = Path(
    rospkg.RosPack().get_path("jupiterobot2_vision_yolov5")
).resolve()
package_scripts = package_path / "scripts"
workspace_root = Path(
    os.environ.get("EKD_CATKIN_WS", package_path.parents[3])
).resolve()
if not (package_scripts / "detector.py").is_file():
    raise RuntimeError(f"SafeZone detector module not found in {package_scripts}")
sys.path.insert(0, str(package_scripts))

from detector import DEFAULT_DATA, DEFAULT_WEIGHTS, Detector


TARGETS = {"scissors", "earbuds"}
UNSAFE_CONTEXT_TERMS = (
    "identity",
    "identify",
    "gender",
    "age",
    "male",
    "female",
    "intent",
    "violation",
    "violating",
    "illegal",
    "prohibited",
    "forbidden",
    "not allowed",
    "permitted",
    "compliance",
    "compliant",
    "dangerous",
    "unsafe",
    "danger",
    "risk",
    "hazard",
    "threat",
    "report",
    "non-compliant",
    "noncompliant",
    "breaking rules",
    "sir",
    "madam",
    "injury",
    "injured",
    "bleeding",
    "wearing earbuds",
)
UNSUPPORTED_GENDER_WORDS = re.compile(
    r"\b(?:man|woman|boy|girl|he|she|his|her)\b", re.IGNORECASE
)


class SafeZoneAssistant:
    PREVIEW_WINDOW = "SafeZone live camera"

    def __init__(self):
        rospy.init_node("safezone_assistant")

        self.camera_topic = rospy.get_param(
            "~camera_topic", "/camera/color/image_raw"
        )
        self.processing_interval = float(
            rospy.get_param("~processing_interval", 0.35)
        )
        self.show_preview = bool(rospy.get_param("~show_preview", True))
        if self.processing_interval <= 0:
            raise ValueError("processing_interval must be positive")
        self.policy_mode = rospy.get_param("~policy_mode", "schedule")
        if self.policy_mode not in {"schedule", "work", "off_duty"}:
            raise ValueError(
                "policy_mode must be schedule, work, or off_duty"
            )
        self.work_start = self._parse_schedule_time(
            rospy.get_param("~work_start", ""), "work_start"
        )
        self.work_end = self._parse_schedule_time(
            rospy.get_param("~work_end", ""), "work_end"
        )
        self.breaks = self._parse_breaks(rospy.get_param("~breaks", ""))
        if (self.work_start is None) != (self.work_end is None):
            raise ValueError("work_start and work_end must both be configured")
        if self.work_start is not None and self.work_start == self.work_end:
            raise ValueError("work_start and work_end must be different")

        self.event_directory = Path(
            os.path.expanduser(
                rospy.get_param(
                    "~event_log_dir",
                    str(workspace_root / "output" / "safezone" / "events"),
                )
            )
        )
        try:
            self.event_directory.mkdir(
                parents=True, exist_ok=True, mode=0o700
            )
            os.chmod(self.event_directory, 0o700)
        except OSError as error:
            raise RuntimeError(
                f"Could not create SafeZone event directory "
                f"{self.event_directory}: {error}"
            ) from error
        self.event_log_path = self.event_directory / "events.jsonl"
        self.log_lock = threading.Lock()

        self.bridge = CvBridge()
        self.detector = Detector(
            weights=rospy.get_param("~weights", str(DEFAULT_WEIGHTS)),
            data=rospy.get_param("~data", str(DEFAULT_DATA)),
            conf_thres=float(rospy.get_param("~confidence", 0.25)),
            classes=[0, 1],
            view_img=self.show_preview,
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

        # Optional Qwen context uses the environment key loaded by setup_ekd.bash; YOLO does not need it.
        # Previous key variable: EKD_DASHSCOPE_API_KEY
        api_key = os.environ.get("EKD_QWEN_API_KEY")
        self.client = (
            OpenAI(
                api_key=api_key,
                # Previous endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1
                base_url="https://llm-orqx90gtcezlx878.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
                timeout=45.0,
                max_retries=0,
            )
            if api_key
            else None
        )
        if self.client is None:
            self._status(
                "EKD_QWEN_API_KEY is unset; detections will use the built-in "
                "safety message without Qwen context."
            )

        # Previous model: qwen-omni-turbo
        self.model = rospy.get_param("~qwen_model", "qwen3.8-max")
        self.speech_publisher = rospy.Publisher(
            "/voiceWords", String, queue_size=1
        )
        self.response_publisher = rospy.Publisher(
            "/safezone/response", String, queue_size=1
        )

        self.lock = threading.Lock()
        self.processing = False
        self.received_frame = False
        self.preview_available = self.show_preview
        self.last_inference = 0.0
        self.latest_frame = None
        self.latest_frame_time = None
        self.latest_targets = {}
        self.last_detection_log = {}
        self.camera_subscriber = rospy.Subscriber(
            self.camera_topic,
            Image,
            self._on_image,
            queue_size=1,
            buff_size=10 * 1024 * 1024,
        )
        self.wake_subscriber = rospy.Subscriber(
            "/safezone/wake", String, self._on_wake, queue_size=1
        )
        self.wake_status_subscriber = rospy.Subscriber(
            "/safezone/wake_status",
            String,
            self._on_wake_status,
            queue_size=5,
        )
        rospy.on_shutdown(self._shutdown)
        self._status("Ready. Live camera detection is running continuously.")
        self._status(
            f"Policy profile: {self._policy_status()}. Say a wake phrase to "
            "capture one scene image for feedback."
        )
        self._status(f"Local event log and captured images: {self.event_directory}")
        self._record_event(
            "assistant_started",
            camera_topic=self.camera_topic,
            processing_interval_seconds=self.processing_interval,
            policy_mode=self.policy_mode,
            work_start=str(self.work_start) if self.work_start else None,
            work_end=str(self.work_end) if self.work_end else None,
            breaks=[(str(start), str(end)) for start, end in self.breaks],
            preview_enabled=self.show_preview,
            event_log=str(self.event_log_path),
        )

    @staticmethod
    def _status(message):
        timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
        print(f"[{timestamp}] SafeZone | {message}", flush=True)

    def _record_event(self, event_type, event_id=None, **details):
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(timespec="milliseconds"),
            "event": event_type,
        }
        if event_id is not None:
            entry["event_id"] = event_id
        entry.update(details)
        try:
            with self.log_lock:
                with self.event_log_path.open("a", encoding="utf-8") as log_file:
                    os.chmod(self.event_log_path, 0o600)
                    log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    log_file.flush()
        except OSError as error:
            self._status(f"ERROR: could not write event log: {error}")

    def _on_wake_status(self, message):
        self._status(f"Wake listener | {message.data}")
        self._record_event("wake_listener_status", message=message.data)

    def _on_wake(self, message):
        event_id = uuid.uuid4().hex
        wake_phrase = message.data.strip()
        captured_at = datetime.now().astimezone()
        with self.lock:
            if self.processing:
                self._record_event(
                    "wake_ignored",
                    event_id,
                    wake_phrase=wake_phrase,
                    reason="previous event is still processing",
                )
                self._status("Wake ignored; the previous event is still processing.")
                return
            if self.latest_frame is None:
                self._record_event(
                    "wake_without_camera_frame",
                    event_id,
                    wake_phrase=wake_phrase,
                )
                self._status("Wake received, but no camera frame is available yet.")
                return
            frame = self.latest_frame.copy()
            targets = dict(self.latest_targets)
            frame_time = self.latest_frame_time
            self.processing = True
        policy_mode = self._active_policy_mode(captured_at)

        image_path = self.event_directory / f"{event_id}.jpg"
        try:
            if not cv2.imwrite(str(image_path), frame):
                raise OSError("OpenCV could not save the event image")
            os.chmod(image_path, 0o600)
            saved_image = str(image_path)
        except (OSError, cv2.error) as error:
            saved_image = None
            self._status(f"ERROR: could not save wake-triggered image: {error}")

        self._record_event(
            "wake_capture",
            event_id,
            wake_phrase=wake_phrase,
            policy_mode=policy_mode,
            captured_at=captured_at.isoformat(timespec="seconds"),
            camera_frame_timestamp=frame_time,
            image_path=saved_image,
            detections=targets,
        )
        self._status(
            "Wake phrase recognized. Captured one current frame; "
            "live detection continues."
        )
        worker = threading.Thread(
            target=self._analyze_and_speak,
            args=(event_id, frame, targets, saved_image, policy_mode, captured_at),
            name="safezone-qwen-event",
            daemon=True,
        )
        worker.start()

    def _on_image(self, message):
        now = time.monotonic()
        with self.lock:
            if now - self.last_inference < self.processing_interval:
                return
            self.last_inference = now

        try:
            frame = self.bridge.imgmsg_to_cv2(message, "bgr8")
        except CvBridgeError as error:
            self._status(f"ERROR: could not decode camera frame: {error}")
            return

        try:
            preview, detections = self.detector.detect(frame.copy())
        except (RuntimeError, cv2.error) as error:
            self._status(f"ERROR: detector failed: {error}")
            return

        targets = {}
        for detection in detections:
            label = str(detection.name).strip().lower()
            if label in TARGETS:
                targets[label] = max(
                    targets.get(label, 0.0), float(detection.conf)
                )

        with self.lock:
            self.latest_frame = frame.copy()
            self.latest_frame_time = datetime.now().astimezone().isoformat(
                timespec="milliseconds"
            )
            self.latest_targets = targets

        if not self.received_frame:
            self.received_frame = True
            self._status("Camera feed received; live local detection is active.")
            self._record_event("camera_frame_received")

        if self.preview_available:
            try:
                cv2.putText(
                    preview,
                    "SAFEZONE LIVE - image upload only after wake phrase",
                    (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow(self.PREVIEW_WINDOW, preview)
                cv2.waitKey(1)
            except cv2.error as error:
                self.preview_available = False
                self._status(
                    "Live camera preview unavailable; detection continues without a "
                    f"window ({error})."
                )

        self._report_live_detections(targets)

    def _report_live_detections(self, targets):
        now = time.monotonic()
        for name, score in targets.items():
            if now - self.last_detection_log.get(name, 0.0) < 30.0:
                continue
            self.last_detection_log[name] = now
            self._status(
                f"Live detection: possible {name} (confidence {score:.2f}); "
                "waiting for a wake phrase before sending an image."
            )
            self._record_event(
                "live_detection",
                label=name,
                confidence=round(score, 4),
            )

    def _analyze_and_speak(
        self, event_id, frame, targets, image_path, policy_mode, captured_at
    ):
        context = ""
        qwen_response = ""
        qwen_status = "skipped_no_api_key"
        qwen_error = None
        try:
            try:
                if self.client is not None:
                    qwen_response, context = self._get_visual_context(
                        frame, targets, policy_mode, captured_at
                    )
                    qwen_status = "success"
            except APIError as error:
                qwen_status = "error"
                qwen_error = str(error)
                self._status(f"Qwen API error: {error}")
            except (ValueError, cv2.error) as error:
                qwen_status = "error"
                qwen_error = str(error)
                self._status(f"Could not prepare the event image: {error}")

            message = self._safety_message(
                targets, policy_mode, context, captured_at
            )
            self.response_publisher.publish(String(data=message))
            self.speech_publisher.publish(String(data=message))
            self._status(f"Spoken response: {message}")
            self._record_event(
                "event_response",
                event_id,
                image_path=image_path,
                detections=targets,
                policy_mode=policy_mode,
                qwen_status=qwen_status,
                qwen_response=qwen_response,
                visual_context=context,
                qwen_error=qwen_error,
                spoken_response=message,
            )
        finally:
            with self.lock:
                self.processing = False

    def _get_visual_context(self, frame, targets, policy_mode, captured_at):
        encoded_ok, encoded_image = cv2.imencode(
            ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        )
        if not encoded_ok:
            raise ValueError("OpenCV could not encode the captured event frame")

        image_data = base64.b64encode(encoded_image.tobytes()).decode("ascii")
        target_summary = "\n".join(
            (
                f"- {name}: DETECTED (YOLO confidence "
                f"{targets[name]:.2f})"
                if name in targets
                else f"- {name}: NOT DETECTED"
            )
            for name in sorted(TARGETS)
        )
        if policy_mode == "work":
            policy_summary = (
                "Active policy at capture: WORK TIME. The configured local demo "
                "rule treats detected scissors and earbuds as prohibited during "
                "duty. The local policy module, not you, generates the final "
                "compliance warning."
            )
        elif policy_mode == "off_duty":
            policy_summary = (
                "Active policy at capture: OFF DUTY. The work-time prohibition is "
                "not active; do not describe either detected object as prohibited."
            )
        else:
            policy_summary = (
                "Active policy at capture: SCHEDULE UNCONFIGURED. Do not claim "
                "that a work-time prohibition is active."
            )
        prompt = (
            f"Capture time (robot local time): {captured_at.isoformat(timespec='seconds')}.\n"
            f"Selected policy profile: {self.policy_mode}.\n{policy_summary}\n"
            "Current-frame local detector results:\n"
            f"{target_summary}\n"
            "Describe the visible scene neutrally in at most 25 words. "
            "Mention only clearly visible location, posture, and unambiguous "
            "clothing or headwear colors. Do not identify a person, infer gender, "
            "age, movement, intent, danger, injury, rule compliance, or claim an "
            "object belongs to or is being used by someone unless unmistakably "
            "visible. Detection of earbuds does not prove they are being worn. "
            "Do not give a policy warning or thank-you; the local safety policy "
            "module will create the spoken response. Return only the brief scene "
            "description, or 'No person or target is clearly visible.'"
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
            self._status("Qwen returned no plain-text visual context.")
            return "", ""

        qwen_response = content.strip()
        context = " ".join(qwen_response.split()).strip(" .")
        if not context or len(context.split()) > 25 or len(context) > 240:
            self._status("Ignoring empty or overly long Qwen scene description.")
            return qwen_response, ""
        lowered = context.lower()
        if (
            any(term in lowered for term in UNSAFE_CONTEXT_TERMS)
            or UNSUPPORTED_GENDER_WORDS.search(context)
        ):
            self._status("Ignoring Qwen context with unsupported safety conclusions.")
            return qwen_response, ""
        self._status(f"Qwen scene context: {context}")
        return qwen_response, context

    def _close_preview(self):
        if not self.show_preview:
            return
        try:
            cv2.destroyWindow(self.PREVIEW_WINDOW)
        except cv2.error:
            pass

    @staticmethod
    def _parse_schedule_time(value, name):
        value = str(value).strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%H:%M").time()
        except ValueError as error:
            raise ValueError(f"{name} must use 24-hour HH:MM format") from error

    @classmethod
    def _parse_breaks(cls, value):
        breaks = []
        for item in str(value).split(","):
            item = item.strip()
            if not item:
                continue
            parts = item.split("-")
            if len(parts) != 2:
                raise ValueError(
                    "breaks must be comma-separated HH:MM-HH:MM ranges"
                )
            start = cls._parse_schedule_time(parts[0], "break start")
            end = cls._parse_schedule_time(parts[1], "break end")
            if start == end:
                raise ValueError("break start and end must be different")
            breaks.append((start, end))
        return breaks

    @staticmethod
    def _within_time_range(now, start, end):
        current = now.timetz().replace(tzinfo=None)
        if start < end:
            return start <= current < end
        return current >= start or current < end

    def _active_policy_mode(self, captured_at):
        if self.policy_mode in {"work", "off_duty"}:
            return self.policy_mode
        if self.work_start is None or self.work_end is None:
            return "schedule_unconfigured"
        in_work_hours = self._within_time_range(
            captured_at, self.work_start, self.work_end
        )
        in_break = any(
            self._within_time_range(captured_at, start, end)
            for start, end in self.breaks
        )
        return "work" if in_work_hours and not in_break else "off_duty"

    def _policy_status(self):
        if self.policy_mode == "schedule":
            if self.work_start is None:
                return "schedule selected but duty hours are not configured; advisory only"
            breaks = ", ".join(
                f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
                for start, end in self.breaks
            ) or "no configured breaks"
            return (
                f"schedule-based ({self.work_start.strftime('%H:%M')}-"
                f"{self.work_end.strftime('%H:%M')}, breaks: {breaks}, local time; "
                f"currently {self._active_policy_mode(datetime.now().astimezone())})"
            )
        return f"{self.policy_mode.replace('_', '-')} demo override"

    @staticmethod
    def _safety_message(targets, policy_mode, visual_context, captured_at):
        items = " and ".join(
            name for name in ("scissors", "earbuds") if name in targets
        )
        timestamp = captured_at.strftime("%H:%M")
        scene = (
            f"Scene: {visual_context}. " if visual_context else ""
        )
        saved = (
            f"This scene image was saved locally at {timestamp} for safety review. "
        )
        if not targets:
            if policy_mode == "work":
                return (
                    f"{scene}No prohibited target was detected in this frame. "
                    "Thank you for following the active-duty safety rules."
                )
            if policy_mode == "off_duty":
                return (
                    f"{scene}No scissors or earbuds were detected. Thank you "
                    "for helping keep the workspace safe."
                )
            return (
                f"{scene}No scissors or earbuds were detected. Thank you for "
                "helping keep the workspace safe."
            )

        if policy_mode == "work":
            reasons = []
            if "scissors" in targets:
                reasons.append(
                    "secure the scissors and keep tools clear of moving machinery"
                )
            if "earbuds" in targets:
                reasons.append(
                    "put away personal earbuds and keep required hearing protection "
                    "and equipment alarms in mind"
                )
            return (
                f"{scene}Attention, team: possible {items} detected. The active-duty "
                "work-time policy prohibits these items during duty. Please "
                f"{' and '.join(reasons)} and follow site safety procedures. "
                f"{saved}"
            )

        if policy_mode == "off_duty":
            return (
                f"{scene}Possible {items} detected. The off-duty demo profile is "
                "active, so the work-time restriction is not being applied. "
                "Please still follow equipment and site safety guidance."
            )

        return (
            f"{scene}Possible {items} detected, but duty hours are not configured, "
            "so SafeZone cannot determine whether the work-time prohibition is "
            "active. Please follow site safety guidance. "
            f"{saved}"
        )

    def _shutdown(self):
        self.camera_subscriber.unregister()
        self._close_preview()


if __name__ == "__main__":
    SafeZoneAssistant()
    rospy.spin()
