#!/usr/bin/env python3

import re
import time

import gi
import rospy
from std_msgs.msg import Empty

gi.require_version("Gst", "1.0")
from gi.repository import Gst


class SafeZoneWakeListener:
    def __init__(self):
        rospy.init_node("safezone_wake")
        Gst.init(None)

        self.keyword = self._normalize(rospy.get_param("~keyword", "hey ekd"))
        self.cooldown = rospy.get_param("~cooldown_seconds", 3.0)
        source = rospy.get_param("~source", "alsasrc")
        acoustic_model = rospy.get_param(
            "~hmm", "/usr/local/share/pocketsphinx/model/en-us/en-us"
        )
        dictionary = rospy.get_param("~dict")
        keywords = rospy.get_param("~kws")

        self.publisher = rospy.Publisher("/safezone/wake", Empty, queue_size=1)
        self.last_wake = 0.0
        pipeline_description = (
            f"{source} ! audioconvert ! audioresample ! "
            "audio/x-raw,format=S16LE,channels=1,rate=16000 ! "
            "pocketsphinx name=asr ! fakesink"
        )
        self.pipeline = Gst.parse_launch(pipeline_description)
        self.recognizer = self.pipeline.get_by_name("asr")
        self.recognizer.set_property("hmm", acoustic_model)
        self.recognizer.set_property("dict", dictionary)
        self.recognizer.set_property("kws", keywords)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::element", self._on_element_message)
        self.bus.connect("message::error", self._on_error)
        rospy.on_shutdown(self.shutdown)

        result = self.pipeline.set_state(Gst.State.PLAYING)
        if result == Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("PocketSphinx could not start the microphone pipeline")
        rospy.loginfo("Listening locally for the wake phrase: %s", self.keyword)

    @staticmethod
    def _normalize(text):
        return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())

    def _on_element_message(self, _bus, message):
        structure = message.get_structure()
        if structure is None or not structure.has_field("final"):
            return
        if not structure.get_value("final"):
            return

        hypothesis = self._normalize(structure.get_value("hypothesis") or "")
        if hypothesis != self.keyword:
            return

        now = time.monotonic()
        if now - self.last_wake < self.cooldown:
            return
        self.last_wake = now
        rospy.loginfo("SafeZone wake phrase detected")
        self.publisher.publish(Empty())

    @staticmethod
    def _on_error(_bus, message):
        error, debug = message.parse_error()
        rospy.logerr("PocketSphinx audio pipeline failed: %s (%s)", error, debug)
        rospy.signal_shutdown("PocketSphinx audio pipeline failed")

    def shutdown(self):
        self.pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    SafeZoneWakeListener()
    rospy.spin()
