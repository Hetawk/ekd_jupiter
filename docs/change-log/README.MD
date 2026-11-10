# EKD Catkin Workspace Change Log

See [changes.md](./changes.md) for the chronological workspace change history, including configuration changes and their validation notes.

The latest entries record the SafeZone and chatbot Qwen Max update, camera/logging improvements, assistant import fix, removal of the unused `Wunti` scaffold, quieting the PocketSphinx startup dump, expanded wake phrases with deterministic phrase matching, continuous local detection, wake-triggered image/event logging under the Git-ignored workspace `output/` directory, playback-confirmed TTS with explicit failure reporting, and selectable schedule/work/off-duty policy profiles. The active model is `qwen3.8-max`; the required MAAS `BASE_URL` remains unchanged. The schedule's current demo default is every day 09:00-17:00 local time with a 12:00-13:00 lunch break; verify site-specific policy and validate alerts on the robot before operational use.
