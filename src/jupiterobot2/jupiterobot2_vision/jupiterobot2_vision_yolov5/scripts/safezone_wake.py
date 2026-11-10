#!/usr/bin/env python3

from contextlib import contextmanager
from datetime import datetime
import os
import re
import threading
import time
from pathlib import Path

import gi
import rospy
from std_msgs.msg import String

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


@contextmanager
def _quiet_pocketsphinx_initialization():
    saved_stderr = os.dup(2)
    null_stderr = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null_stderr, 2)
        yield
    finally:
        os.dup2(saved_stderr, 2)
        os.close(null_stderr)
        os.close(saved_stderr)


class SafeZoneWakeListener:
    def __init__(self):
        rospy.init_node("safezone_wake")
        Gst.init(None)

        keyword_file = rospy.get_param("~kws")
        self.keywords = self._load_keywords(keyword_file)
        self.cooldown = rospy.get_param("~cooldown_seconds", 3.0)
        source = rospy.get_param("~source", "alsasrc")
        acoustic_model = rospy.get_param(
            "~hmm", "/usr/local/share/pocketsphinx/model/en-us/en-us"
        )
        dictionary = rospy.get_param("~dict")
        keywords = rospy.get_param("~kws")

        self.publisher = rospy.Publisher("/safezone/wake", String, queue_size=1)
        self.status_publisher = rospy.Publisher(
            "/safezone/wake_status", String, queue_size=5, latch=True
        )
        self.last_wake = 0.0
        self.last_unmatched_report = 0.0
        self.audio_seen = False
        self.quiet_since = time.monotonic()
        self.quiet_warning_sent = False
        pipeline_description = (
            f"{source} ! audioconvert ! audioresample ! "
            "audio/x-raw,format=S16LE,channels=1,rate=16000 ! "
            "level name=mic_level interval=1000000000 post-messages=true ! "
            "pocketsphinx name=asr ! fakesink"
        )
        with _quiet_pocketsphinx_initialization():
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
        self.mainloop = GLib.MainLoop()
        self.mainloop_thread = threading.Thread(
            target=self.mainloop.run, name="safezone-gst-bus", daemon=True
        )
        self.mainloop_thread.start()
        phrase_list = ", ".join(sorted(self.keywords))
        self._status(
            f"Listening on {source} for: {phrase_list}. "
            "The live camera is already active; a wake phrase saves one scene image."
        )

    @classmethod
    def _load_keywords(cls, keyword_file):
        keywords = set()
        with Path(keyword_file).open(encoding="utf-8") as file:
            for line in file:
                phrase = line.partition("/")[0].strip()
                if phrase:
                    keywords.add(cls._normalize(phrase))
        if not keywords:
            raise ValueError(f"No wake phrases found in {keyword_file}")
        return keywords

    def _status(self, message):
        self.status_publisher.publish(String(data=message))

    @staticmethod
    def _normalize(text):
        return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())

    def _match_keyword(self, hypothesis):
        heard_words = hypothesis.split()
        matches = []
        phrases = sorted(self.keywords)
        for phrase in phrases:
            phrase_words = phrase.split()
            phrase_length = len(phrase_words)
            for start in range(len(heard_words) - phrase_length + 1):
                if heard_words[start:start + phrase_length] == phrase_words:
                    matches.append((start, -phrase_length, phrase))
        return min(matches)[2] if matches else None

    def _on_element_message(self, _bus, message):
        structure = message.get_structure()
        if structure is None:
            return
        if structure.get_name() == "level":
            self._on_audio_level(structure)
            return
        if not structure.has_field("final"):
            return
        if not structure.get_value("final"):
            return

        hypothesis = self._normalize(structure.get_value("hypothesis") or "")
        matched_keyword = self._match_keyword(hypothesis)
        if matched_keyword is None:
            now = time.monotonic()
            if hypothesis and now - self.last_unmatched_report >= 3.0:
                self.last_unmatched_report = now
                self._status(
                    f"Heard '{hypothesis}', but it is not one of the wake phrases."
                )
            return

        now = time.monotonic()
        if now - self.last_wake < self.cooldown:
            return
        self.last_wake = now
        if matched_keyword != hypothesis:
            self._status(
                f"Heard '{hypothesis}'; matched wake phrase '{matched_keyword}'."
            )
        else:
            self._status(f"Wake phrase recognized: '{matched_keyword}'.")
        self.publisher.publish(String(data=matched_keyword))

    def _on_audio_level(self, structure):
        levels = structure.get_value("rms")
        try:
            level_db = max(float(level) for level in levels)
        except (TypeError, ValueError):
            return

        now = time.monotonic()
        if level_db > -55.0:
            self.quiet_since = now
            self.quiet_warning_sent = False
            if not self.audio_seen:
                self.audio_seen = True
                self._status(
                    f"Microphone audio detected (input level {level_db:.0f} dBFS)."
                )
        elif not self.quiet_warning_sent and now - self.quiet_since >= 5.0:
            self.quiet_warning_sent = True
            self._status(
                f"WARNING: microphone input is very quiet ({level_db:.0f} dBFS). "
                "Check the system's selected PulseAudio input."
            )

    def _on_error(self, _bus, message):
        error, debug = message.parse_error()
        self._status(
            f"ERROR: microphone audio pipeline failed: {error} ({debug})"
        )
        rospy.signal_shutdown("PocketSphinx audio pipeline failed")

    def shutdown(self):
        self.pipeline.set_state(Gst.State.NULL)
        if self.mainloop.is_running():
            self.mainloop.quit()


if __name__ == "__main__":
    SafeZoneWakeListener()
    rospy.spin()
