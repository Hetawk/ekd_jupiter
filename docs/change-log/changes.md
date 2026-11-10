## 2026-11-10: EKD workspace paths

- Updated references to the workspace root and devel setup from `catkin_ws` to `ekd_catkin_ws`.
- Before/after examples: `/home/mustar/catkin_ws/...` became `/home/mustar/ekd_catkin_ws/...`; `~/catkin_ws/devel/setup.bash` became `~/ekd_catkin_ws/devel/setup.bash`. VS Code include/interpreter paths, launcher commands, GUI commands, map references, and the OpenVINO model directory now resolve against the EKD copy.
- The original versions remain in the untouched `~/catkin_ws` tree. The EKD copy contains only the active EKD paths; generated artifacts and unrelated CI references were not rewritten.
- Scope was limited to this `ekd_catkin_ws` copy; the original `catkin_ws` was not modified.
- Kept `.travis.sh` and generated `Ui_Robot.py` unchanged.
- Updated files:
  - `maps/JupiterOfficeSim.yaml`
  - `maps/simple.yaml`
  - `maps/test.yaml`
  - `.vscode/c_cpp_properties.json`
  - `.vscode/settings.json`
  - `src/rfa-speech/.vscode/c_cpp_properties.json`
  - `src/rfa-speech/.vscode/settings.json`
  - `src/rfa-speech/rfa_gpt/.vscode/c_cpp_properties.json`
  - `src/rfa-speech/rfa_gpt/.vscode/settings.json`
  - `src/jupiterobot2/jupiterobot2_gazebo/launch/jupiterobot2_world.launch`
  - `src/jupiterobot2/jupiterobot2_apps/jupiterobot2_move_grasp/launch/gpsr_drivers.launch`
  - `src/jupiterobot2/jupiterobot2_qt/qwen_ros/.vscode/c_cpp_properties.json`
  - `src/jupiterobot2/jupiterobot2_qt/qwen_ros/.vscode/settings.json`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_qt/launch_qt.sh`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_qt/scripts/cmds.py`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_qt/scripts/Robot_main.py`
  - `src/jupiterobot2/jupiterobot2_qt/hand_slice_game/.vscode/c_cpp_properties.json`
  - `src/jupiterobot2/jupiterobot2_qt/hand_slice_game/.vscode/settings.json`
  - `src/jupiterobot2/jupiterobot2_qt/.vscode/c_cpp_properties.json`
  - `src/jupiterobot2/jupiterobot2_qt/.vscode/settings.json`
  - `src/jupiterobot2/jupiterobot2_qt/desktop_start/Jupiter2_GUI.py`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_gesture_game/.vscode/c_cpp_properties.json`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_gesture_game/.vscode/settings.json`
  - `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_openvino/src/interactive_face_ros.cpp`
  - `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_openvino/src/.vscode/c_cpp_properties.json`
  - `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_openvino/src/.vscode/settings.json`
- Build validation was not run by this script.
- To build: `cd ~/ekd_catkin_ws && source /opt/ros/noetic/setup.bash && catkin_make`.

## 2026-11-10: Fresh EKD catkin build

- Cause: copied CMake cache referenced `/home/mustar/catkin_ws`.
- Recovery: moved EKD build and devel directories to timestamped backups; original `catkin_ws` was untouched.
- Result: `catkin_make` completed successfully and EKD devel setup was sourced.

## 2026-11-10: EKD-specific shell setup and workflow

- Added `setup_ekd.bash` to source ROS Noetic and this workspace's devel environment from any working directory.
- Updated `COMMANDS.md` to recommend the EKD helper and to use timestamped build/devel backups instead of deleting generated directories.
- Kept `~/.bashrc` unchanged, so the original workspace remains the default for new terminals; source the EKD helper when working in EKD.
- Validation: `bash -n setup_ekd.bash` passed; sourcing it set `EKD_CATKIN_WS=/home/mustar/ekd_catkin_ws`, and `rospack find` resolved `jupiterobot2_bringup` and `astra_camera` inside EKD. The EKD `catkin_make` build also exited successfully with code 0.

## 2026-11-10: EKD SafeZone YOLOv5

- Created `~/ekd_yolov5/` by extracting the `safezone/` tree from `~/Downloads/safezone.zip`; excluded the archive's `__MACOSX/` metadata. The existing `~/yolov5/` was not modified.
- Before: the original detector root was `Path(__file__).resolve().parents[6] / 'yolov5'`, with `yolov5s.pt` and `data/coco128.yaml` defaults.
- After: the EKD detector root is `Path.home() / 'ekd_yolov5'`, with `weights/safezone_best.pt` as the short runtime path and `data/sz-mod.yaml` (`scissors`, `earbuds`). The runtime weight is a relative symlink to the documented primary 100-epoch checkpoint under `analysis/`; the archived original is retained. The former YOLO settings are retained as comments next to the active EKD settings in the four detector files.
- Files modified:
  - `COMMANDS.md`
  - `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/detector.py`
  - `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/detector_cn.py`
  - `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/detect.py`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_qt/scripts/yolo_scripts/detector_cn.py`
  - `~/ekd_yolov5/weights/safezone_best.pt` (relative symlink to the archived checkpoint)
  - `docs/change-log/changes.md`
- Commands run:
  - `unzip -l /home/mustar/Downloads/safezone.zip`
  - `unzip -t /home/mustar/Downloads/safezone.zip`
  - Guarded extraction: `unzip -q "$HOME/Downloads/safezone.zip" 'safezone/*' -d "$HOME"` followed by `mv "$HOME/safezone" "$HOME/ekd_yolov5"`.
  - Created the runtime alias with `mkdir -p "$HOME/ekd_yolov5/weights"` and `ln -s ../analysis/sz-mod-training-2026-11-09/training/weights/best.pt "$HOME/ekd_yolov5/weights/safezone_best.pt"`.
  - `PYTHONPYCACHEPREFIX=/tmp/ekd-yolov5-pycache python3 -m py_compile` on the four detector files listed above.
  - Checked that the selected checkpoint and `data/sz-mod.yaml` exist and that no detector retains the old `yolov5s.pt` or `coco128.yaml` defaults.
- Validation passed: the archive passed `unzip -t`, the required code/config/checkpoint files exist, the runtime symlink resolves to the archived checkpoint, and all four modified Python scripts compile. Full ROS camera/model inference was not run.

## Change record convention

- For a small, hand-maintained code setting that is intentionally redirected for EKD, keep the original setting as a concise comment beside the active EKD value.
- Do not duplicate large config blocks or generated files as comments. Keep their original versions in `~/catkin_ws` and record the before/after paths and every affected EKD file in this log.
- Add every command used for copying, building, or validating under the relevant dated entry, and keep repeatable operational commands in `COMMANDS.md`.

## 2026-11-10: Replace course guide PDF and add presentation source

- Replaced `docs/course-guide.pdf` with the readable conversion from `~/Downloads/ml_course_guide.pdf`.
- Added `docs/course-guide.pptx` from `~/Downloads/ml_course_guide.pptx` so the source presentation is stored beside the PDF.
- Commands run:
  - `cp /home/mustar/Downloads/ml_course_guide.pdf /home/mustar/ekd_catkin_ws/docs/course-guide.pdf`
  - `cp /home/mustar/Downloads/ml_course_guide.pptx /home/mustar/ekd_catkin_ws/docs/course-guide.pptx`
  - `cmp -s` on each source/destination pair.
  - `pdfinfo docs/course-guide.pdf`, `unzip -t docs/course-guide.pptx`, and `pdftotext -layout docs/course-guide.pdf -` with a ROS-command search.
- Validation passed: both copies match their Downloads sources; the PDF is 104 pages and command text extracts; the PPTX archive passes integrity testing.

## 2026-11-10: Add SafeZone about document to EKD docs

- Moved `~/Downloads/about.md` to `docs/about.md`; the source path no longer exists.
- Command run: `mv /home/mustar/Downloads/about.md /home/mustar/ekd_catkin_ws/docs/about.md`.
- Validation passed: the destination exists and the Downloads source path is absent; the file size is 34,537 bytes.
- Updated `COMMANDS.md` with the repeatable move command.

## 2026-11-10: Map course-guide commands to EKD

- Added original `catkin_ws` and EKD command pairs to `COMMANDS.md` for build/GUI, speech/chatbot, cameras/photo capture, OpenCV, YOLO, MediaPipe, and VLM workflows.
- Corrected the EKD photo-capture package mapping: the PDF says `rchomeedu_vision`, which is absent from EKD; the equivalent scripts are in `rfa_vision`.
- Added notes for robot camera/topic selection, chatbot API credentials, conceptual-only exercises, the custom YOLO training slide, and the non-fatal `Wunti` naming warning that existed at the time. The unused package was later removed; see the SafeZone startup-fix entry below.
- Commands run to read the guide and validate EKD commands:
  - `pdftotext -layout -nopgbrk docs/course-guide.pdf -` with ROS-command searches and focused slide ranges.
  - `source ~/ekd_catkin_ws/setup_ekd.bash && rospack find <package>` for the guide packages.
  - `roslaunch --nodes <package> <launch_file>` for the GUI, speech, chatbot, camera, OpenCV, YOLO, and MediaPipe launch files.
  - `rosrun --prefix /bin/true <package> <script>` for the EKD photo and VLM scripts; checked the voice binary paths under `devel/lib`.
- Validation passed: all listed EKD launch files parsed and the checked scripts/binaries resolved. No camera, speech, GUI, LLM request, or inference node was started; hardware/API runtime behavior remains to be tested on the robot.

## 2026-11-10: Move EKD chatbot credentials to local environment

- Migrated the OpenAI and Qwen API-key values from the EKD copies of `src/rfa-speech/rfa_gpt/config/var.yaml` and `qwen.yaml` into the root `ekd_catkin_ws/.env`, created with owner-only mode `600`.
- The EKD DeepSeek YAML contained only a placeholder; its `.env` variable is empty until configured.
- Removed `OPENAI_API_KEY` fields from the three EKD YAML configs. Their endpoint, model, and prompt settings remain in YAML. The corresponding files under the original `catkin_ws` were not modified.
- Updated `setup_ekd.bash` to source `.env`, added `/.env` to the EKD root `.gitignore`, and updated `deepseek_call.py`, `qwen_call.py`, and `gpt_call.py` to read `EKD_DEEPSEEK_API_KEY`, `EKD_QWEN_API_KEY`, and `EKD_OPENAI_API_KEY` respectively, failing clearly if a required variable is unset.
- Updated `COMMANDS.md` with the environment-variable names and local editing instructions; no credential values were added to documentation.
- EKD files changed:
  - `.env` (local-only, ignored, mode `600`; no values recorded here)
  - `.gitignore`
  - `setup_ekd.bash`
  - `src/rfa-speech/rfa_gpt/config/var.yaml`
  - `src/rfa-speech/rfa_gpt/config/deepseek.yaml`
  - `src/rfa-speech/rfa_gpt/config/qwen.yaml`
  - `src/rfa-speech/rfa_gpt/scripts/gpt_call.py`
  - `src/rfa-speech/rfa_gpt/scripts/deepseek_call.py`
  - `src/rfa-speech/rfa_gpt/scripts/qwen_call.py`
  - `COMMANDS.md`
  - `docs/change-log/changes.md`
- Commands run: one-off PyYAML migration from EKD config files into `.env` without printing values; `sed -i '/^[[:space:]]*OPENAI_API_KEY[[:space:]]*:/d'` on the three EKD YAML files; `stat` and a source/match check for `.env`; `bash -n setup_ekd.bash`; and `python3 -m py_compile` on the three changed GPT client scripts.
- Validation passed: the migrated OpenAI/Qwen values matched their EKD sources before scrubbing, `.env` is mode `600`, the EKD helper loads both configured variables, the YAML files parse without credential fields, all three client scripts compile, and both configured clients initialize without making network calls. The unset DeepSeek credential produces the expected error.
- Mapping cross-check: compared the untouched original `catkin_ws` configs against the EKD environment by equality without displaying values. `var.yaml` (`gpt-4o-mini`, OpenAI endpoint) matches `EKD_OPENAI_API_KEY`; `qwen.yaml` (`qwen-plus`, Qwen-compatible endpoint) matches `EKD_QWEN_API_KEY`, despite its legacy `OPENAI_API_KEY` field name; `deepseek.yaml` remains a placeholder with no key match.

## 2026-11-10: GitHub publish preparation

- Expanded root `.gitignore` for Catkin build/devel/install/log outputs, timestamped build backups, Python caches, CMake output, `.env`, and nested `.git` metadata.
- Moved the 12 nested repository `.git` directories to `/home/mustar/ekd_catkin_ws_git_metadata_backup_20261110-075400` (mode `700`) so the EKD parent repository can include their source files instead of recording gitlinks. Histories remain recoverable from that external backup.
- `git add --dry-run` confirmed representative formerly nested repositories now list ordinary files. No files have been staged, committed, or pushed.
- Moved additional hardcoded EKD credentials from Qt DashScope/Qwen, RFA VLM, Spark, and iFlytek TTS scripts into `.env` with separate provider variables. Removed the Qt Qwen YAML key field and changed the RFA VLM placeholder clients to use environment variables. Updated the complete variable map in `COMMANDS.md`.
- Changed source files include:
  - `src/jupiterobot2/jupiterobot2_qt/qwen_ros/scripts/qwen_call.py`
  - `src/jupiterobot2/jupiterobot2_qt/qwen_ros/scripts/qwen_img_describe.py`
  - `src/jupiterobot2/jupiterobot2_qt/qwen_ros/scripts/qwen_wanx.py`
  - `src/jupiterobot2/jupiterobot2_qt/qwen_ros/config/qwen.yaml`
  - `src/rfa-vision/rfa_vlm/scripts/image_recognition.py`
  - `src/rfa-vision/rfa_vlm/scripts/image_recognition_qwen.py`
  - `src/rfa-vision/rfa_vlm/scripts/object_detection.py`
  - `src/rfa-vision/rfa_vlm/scripts/object_detection_qwen.py`
  - `src/jupiterobot2/jupiterobot2_apps/jupiterobot2_spark/scripts/spark_demo.py`
  - `src/jupiterobot2/jupiterobot2_apps/jupiterobot2_spark/scripts/tts_ws_python3_demo.py`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_qt/scripts/tts_qwen.py`
  - `src/jupiterobot2/jupiterobot2_qt/jupiterobot2_qt/scripts/xf_tts.py`
- Validation: generated output and `.env` ignore rules verified; moved nested metadata count and backup permissions verified; edited Python scripts compile; a whole-workspace scan found no likely literal credential values outside `.env` and ignored generated/nested-Git content. Credential values previously shown in chat must be rotated before publishing.
- Push blocker: `Robot_main.py` uses `resource/jupiter2_sim_nav_show.mp4`, which is 104,062,721 bytes and exceeds GitHub's 100 MB file limit. Git LFS is not installed; do not stage/push until this asset is handled with LFS or an agreed external-download approach.
- Portability note at the time of this entry: the EKD detector scripts referenced sibling `~/ekd_yolov5`; this was resolved in the following bundled-model entry.

## 2026-11-10: Bundle SafeZone YOLO into central project

- Moved the 154 MB `~/ekd_yolov5` directory into `ekd_catkin_ws/ekd_yolov5` so one clone contains the model source, dataset, analysis artifacts, and selected checkpoint.
- Updated all four EKD detector roots to resolve the bundled directory relative to the workspace root; corrected the Qt detector's workspace parent calculation.
- Updated SafeZone extraction, verification, inference, and training-note paths in `COMMANDS.md`.
- Commands run: guarded `mv /home/mustar/ekd_yolov5 /home/mustar/ekd_catkin_ws/ekd_yolov5`; checked model source, data YAML, and relative checkpoint symlink; `python3 -m py_compile` on all four detector scripts; verified each detector resolves the bundled model directory.
- Validation passed: the model checkpoint symlink resolves inside the repository and all detector scripts compile. The original `~/yolov5` remains unchanged.

## 2026-11-10: Prepare single-clone EKD deployment

- Added `.env.example` with variable names only and `deployment/README.md` with fresh-machine ROS Noetic, rosdep, Git LFS, environment, and build steps.
- Added `.gitattributes` to track the required 104 MB `jupiter2_sim_nav_show.mp4` with Git LFS.
- Bundled `ekd_yolov5/` at the repository root and updated detector paths and `COMMANDS.md` to use the self-contained layout.
- Added a note that nested repository histories are excluded; their metadata is backed up outside the workspace while their source files are included by the parent repo.
- No commit or push was made. Git LFS is not installed yet, and exposed API credentials still need rotation before publishing.

## 2026-11-10: Route VLM object detection through EKD Qwen endpoint

- Updated `src/rfa-vision/rfa_vlm/scripts/object_detection.py` and `image_recognition.py` to use `qwen3.8-max`, matching `image_recognition_qwen.py` on the same Qwen-compatible endpoint and `EKD_QWEN_API_KEY`.
- Kept the previous `gpt-4o-mini` model and former OpenAI base URL as comments; no credential value was added to source.
- Validation: confirmed the EKD Qwen variable is available without printing its value; Python syntax check passed for both changed scripts.

## 2026-11-10: Align SafeZone and chatbot Qwen Max settings

- Changed `src/rfa-speech/rfa_gpt/config/qwen.yaml` from `qwen-plus` to `qwen3.8-max`; retained `qwen-plus` as a comment. The configured `BASE_URL` remains exactly `https://llm-orqx90gtcezlx878.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`.
- Changed SafeZone's Qwen image-context configuration in `src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/safezone_assistant.py` from the DashScope endpoint, `EKD_DASHSCOPE_API_KEY`, and `qwen-omni-turbo` to the same configured MAAS endpoint, `EKD_QWEN_API_KEY`, and `qwen3.8-max`. The previous endpoint, key-variable name, and model are retained as comments.
- Alibaba Cloud's [Model Studio text-generation documentation](https://help.aliyun.com/zh/model-studio/text-generation-model) lists `qwen3.8-max` as the Max model and confirms Max accepts image input.
- Updated `about.md` and `COMMANDS.md` to document the SafeZone demo flow, one-terminal launch, Qwen configuration, and remaining hardware-validation limits.
- Pre-test validation: `catkin_make` completed successfully; `roslaunch --nodes jupiterobot2_vision_yolov5 safezone_demo.launch` resolved the camera, wake listener, assistant, and TTS nodes; the checkpoint loaded and ran local inference on a sample image with only the `scissors` and `earbuds` classes; the PocketSphinx GStreamer pipeline ran on synthetic audio; and `qwen_call.py` passed a mocked completion using the configured URL and `qwen3.8-max`.
- Also confirmed the Qwen YAML's exact `BASE_URL`, Python syntax, SafeZone launch XML, launcher Bash syntax, available ALSA capture-device listings, and `git diff --check`.
- No microphone audio was recorded, no Qwen API request was sent, and no robot camera or speaker session was run. Those checks remain for the supervised on-robot test.

## 2026-11-10: Improve SafeZone camera startup and operator feedback

- The first robot launch repeatedly tried to open two Astra cameras whose configured serials did not match the connected camera (`ADAE723004E`). Replaced the two-camera bring-up with one Astra camera, defaulting to the observed serial and allowing it to be overridden with the `camera_serial_number` launch argument.
- Routed camera-driver and TTS node output to ROS log files instead of the interactive terminal.
- Added a local preview window during the wake-triggered camera window only, with target boxes and `Q`/`Esc` to stop capture early; no preview is kept open outside the active window.
- Replaced routine ROS console messages in the SafeZone wake and assistant nodes with concise local-time status messages, including camera-feed arrival, detections, accepted Qwen context, API failures, and the exact safety message published for speech.
- Added a timestamped startup instruction to `docs/safezone.sh`.
- Updated `COMMANDS.md` and `about.md` with the preview, terminal output, and single-camera behavior.
- Validation: SafeZone launch XML parsed with one camera configured for the serial observed in the pasted log; both Python scripts and the launcher passed syntax checks; `catkin_make` completed successfully; `roslaunch --nodes` resolved the cleanup, camera, wake, assistant, and TTS nodes; and `git diff --check` passed. Live camera preview, microphone capture, Qwen request, and TTS still require a robot run.

## 2026-11-10: Fix SafeZone assistant startup and wake diagnostics

- The robot run showed `safezone_assistant.py` exiting with `ModuleNotFoundError: No module named 'detector'`. Added an explicit ROS package scripts-path lookup before importing the sibling detector module and declared the `rospkg` runtime dependency.
- Routed PocketSphinx's startup configuration dump to the wake node's ROS log file. The wake node now relays concise readiness and microphone-error status over a latched ROS topic, which the assistant timestamps in the terminal.
- This keeps actionable wake status visible while suppressing the long PocketSphinx configuration output.
- Removed the unused `src/Wunti` Catkin tutorial scaffold after confirming it contains only default talker/listener scripts and has no references or dependencies elsewhere in `src`. This removes the `Wunti` package naming warning without renaming or changing a package used by SafeZone.
- Removed the YOLO detector's three import-time debug prints so launching the assistant does not print package/workspace paths.
- Validation: SafeZone assistant imported the ROS-resolved `detector` module; launch XML and Python/Bash syntax checks passed; `catkin_make` completed after package removal; `roslaunch --nodes` resolved the cleanup, camera, wake, assistant, and TTS nodes without the Wunti warning; the ROS package index no longer contains Wunti; and `git diff --check` passed. Live camera preview, microphone capture, Qwen request, and TTS still require robot testing.
- The next robot run confirmed the assistant and wake listener both started, but PocketSphinx's native configuration table still appeared on the terminal. The wake listener now redirects native stderr only while constructing and starting the audio pipeline; subsequent pipeline errors still reach the ROS error callback and SafeZone status output. Its readiness message clarifies that the camera preview opens only after the wake phrase.
- Validation: reproduced the PocketSphinx pipeline using synthetic audio and verified that initialization succeeds without emitting the configuration table; Python syntax, SafeZone launch-node resolution, and `git diff --check` passed. This did not record microphone audio or validate the camera, Qwen, or TTS on the robot.

## 2026-11-10: Expand SafeZone wake phrases and microphone diagnostics

- Added “Hi EKD,” “Hello EKD,” “Hey SafeZone,” “Okay SafeZone,” “SafeZone,” “SafeZone wake up,” and “Wake up SafeZone” as additional PocketSphinx keyword phrases. Phrase matching now accepts every configured keyword, instead of only “Hey EKD.”
- Changed the default audio source from `alsasrc` to `pulsesrc`, which uses the system-selected PulseAudio input; the `audio_source` launch argument remains configurable.
- Added a GStreamer audio-level monitor and concise status for microphone signal, prolonged quiet input, recognized phrases, and occasional unmatched speech. This makes source/phrase problems easier to distinguish without restoring the PocketSphinx configuration flood.
- Added a GLib main loop thread to dispatch GStreamer bus messages while the ROS node is spinning; without a GLib loop, wake results and microphone-level status might never reach the callbacks.
- Updated the SafeZone operational docs with available phrases, audio-source override, and status expectations.
- Validation: all eight KWS phrases have dictionary pronunciations; synthetic audio produced GStreamer microphone-level messages; Python/Bash syntax, launch parsing/node resolution, and whitespace checks passed. Wake recognition from the robot microphone still requires a live test.

## 2026-11-10: Keep SafeZone camera and detection continuously active

- Added three launch policy profiles selected when running `docs/safezone.sh`: schedule-based, work-time demo override, and off-duty demo override. The schedule uses every day with configurable local-robot-time duty hours and breaks; its clearly labeled demo default is 09:00-17:00 with lunch 12:00-13:00. These defaults are not claimed as a universal or verified site standard.
- Added a deterministic local safety-message builder based on the detector's latest wake-triggered frame and selected policy profile. Active work-time detections produce an explicit policy reminder for scissors/earbuds, practical machinery/hearing-awareness guidance, and disclosure that the scene still was saved locally with the capture time. Qwen is used only for optional concise visible scene details and cannot replace a work-time alert when it times out.
- The off-duty profile does not state that the work-time prohibition applies. The schedule-unconfigured profile clearly says the active period cannot be determined. No automatic supervisor reporting occurs.
- Split the Qwen request from policy messaging: it may describe neutral visible location, posture, and unambiguous clothing/headwear colors, without identifying/gendering a person or asserting a doubtful person-object association. Work-time responses use a respectful neutral address and do not infer gender.
- Changed the assistant from wake-gated camera subscription and a 10-second capture window to a persistent camera subscription. Local scissors/earbuds detection and the preview now continue for the whole launch; closing the process closes the camera and preview.
- Changed wake behavior to snapshot the latest in-memory camera frame and detector results, then save and send exactly that still to Qwen. No video or pre-wake frames are written or uploaded. The snapshot is sent even when local detection finds neither target, allowing limited scene feedback.
- Changed the wake ROS message from `std_msgs/Empty` to `std_msgs/String` so the recognized phrase is available in event logs.
- Added append-only JSONL event records for startup, live detections, wake captures, Qwen response/context or API failure, and final spoken response. Wake-triggered stills and the log are stored at `~/.ros/safezone/events/` with user-only file permissions.
- Earlier iteration asked Qwen to compose the entire spoken message, which could fall back to a generic thank-you after a timeout. It now supplies only optional neutral scene details; the local policy module independently builds work-time alerts and detector-based fallback messages.
- Scene details may include clearly visible object location, posture/position, and unambiguous clothing/headwear color, but not identity, gender, intent, or unsupported person-object relationships. The message stays concise; 50 words is a ceiling, not a target.
- Increased the Qwen request timeout from 20 to 45 seconds after the robot log showed the existing timeout expiring during a scene request; detection continues locally while the asynchronous request is in progress.
- Fixed the no-Qwen fallback's target checks to compare the detector-result dictionary's keys, so scissors-only and earbuds-only detections receive the correct message rather than the combined-target warning.
- Corrected preview rendering so target boxes appear on the continuous camera display.
- Updated the SafeZone launch, startup message, command guide, project overview, and change-log summary to describe the persistent camera and wake-only capture/upload behavior.
- Validation: synthetic callback tests confirm continuous local detection, no pre-wake image save, one wake-triggered still, event/response logging, and Qwen message limit/filtering; Python/Bash syntax, launch XML parsing, Catkin build, and diff checks passed. Live camera preview, wake-triggered Qwen API, and TTS still require robot validation.
