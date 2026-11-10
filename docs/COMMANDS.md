# ROS workspace command guide

This file records the commands normally used for the original workspace and the matching commands to use in the duplicated workspace.

## Course-guide copy-and-paste commands

[`course-guide-commands.sh`](./course-guide-commands.sh) is a **copy-and-paste reference, not a launcher**. Do not execute or source the file. The commands are kept inactive so that running it cannot start every node. Choose one task, open the stated number of terminals, and copy the commands for each terminal into that terminal in order. Each command is on its own line; do not join them with `&&`.

To view the command list from the workspace root:

```bash
less docs/course-guide-commands.sh
```

The ROS workflow terminal counts below include one dedicated `roscore` terminal (builds do not need a ROS master). Start one ROS master per session, leave it running, and keep each camera/node terminal open. Every new terminal needs its own workspace setup: use the original setup commands for `~/catkin_ws`, or `source ~/ekd_catkin_ws/setup_ekd.bash` for EKD. The EKD helper selects the modified workspace and loads its local `.env` when present. Although `roslaunch` can start a master automatically, this guide uses a dedicated master so the terminal workflow is explicit and repeatable.

The reference covers the Catkin builds and course-guide ROS examples. Workspace-copy, file-move, archive-extraction, and model-alias setup commands are not included as runnable examples because they are one-time file operations.

For the SafeZone robot demo using the existing checkpoint (no training), run [`safezone.sh`](./safezone.sh) in one terminal. At startup choose exactly one of three policy modes: 1) standard schedule, using fixed daily 09:00-17:00 local robot time with lunch 12:00-13:00; 2) work-time override, always applying work-time reminders for testing; or 3) off-duty override, never applying the work-time prohibition. Option 1 requires no additional time inputs. The work-time override is for testing and does not by itself certify a site policy. The system currently treats scissors and personal earbuds as restricted during the active work-time profile; verify these defaults against the site's approved policy before operational use. The standard times are demo defaults, not a universal industry standard.

The launch starts the single Astra camera by its connected serial number, a local multi-phrase wake listener, continuous local detector, and Jupiter speech output. The live preview and scissors/earbuds detection remain active while the demo runs; frames are held in memory for local processing, not continuously saved or uploaded. Wake phrases include “Hey EKD,” “Hi EKD,” “Hello EKD,” “Hey SafeZone,” “Okay SafeZone,” “SafeZone,” “SafeZone wake up,” and “Wake up SafeZone.” The listener accepts a configured phrase even if PocketSphinx includes other adjacent words in the same hypothesis (for example, “hi ekd hey ekd”). A recognized wake phrase saves and sends exactly one current scene image. While that event is being analyzed/spoken, additional wake triggers are intentionally ignored; once it finishes, the listener remains active for another capture. Before Qwen is asked for optional scene details, its prompt explicitly states the capture time, selected policy profile, effective work/off-duty state, and whether scissors and earbuds were detected (including confidence or “not detected”). The local policy module—not Qwen—creates the work-time or off-duty safety message, so a Qwen timeout does not replace a detected work-time warning with a thank-you. Qwen can add concise visible details such as an object's location, posture/position, or an unambiguous clothing/headwear color, without identifying or gendering a person or asserting an uncertain person-object relationship. Work-time alerts state that the configured policy prohibits detected targets during duty, give a practical safety reminder, and disclose that the wake-triggered scene image was saved locally with its capture time; there is no automatic supervisor reporting. Event images and a JSONL record of wake phrases, selected policy mode, detections, Qwen responses/errors, and spoken responses are stored under `~/ekd_catkin_ws/output/safezone/events/` with user-only file permissions. The workspace ignores `/output/` so private event images/logs are not committed accidentally. The listener uses the selected PulseAudio microphone by default and reports whether audio is reaching it; override the audio source with `audio_source:=alsasrc` if needed. Camera-driver, wake-engine diagnostics, and TTS logs are saved by ROS instead of flooding the terminal. Timestamped SafeZone status messages show wake-listener readiness, microphone warnings, live detections, Qwen scene details, and the exact message sent to speech.

## Recommended EKD workflow

The original workspace remains the default in `~/.bashrc`. To select EKD in a terminal without changing that default, enter the workspace and source its helper once:

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
```

This sources ROS Noetic and the EKD devel environment, and sets `EKD_CATKIN_WS`. It does not modify `~/.bashrc` or the original `catkin_ws`.

Build EKD in one terminal. Run each line separately in that same terminal. Use ROS Noetic directly here: `setup_ekd.bash` requires an already-built `devel/setup.bash`.

```bash
cd ~/ekd_catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make
```

In each new terminal used for EKD, run this setup once before ROS commands. You can then run multiple commands in the same terminal without sourcing again:

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
```

## Course guide files

The editable presentation and readable PDF are stored together in `docs/`. To refresh them from Downloads, copy the converted files using the workspace names below; the PDF copy replaces the existing `docs/course-guide.pdf`:

```bash
cp ~/Downloads/ml_course_guide.pptx ~/ekd_catkin_ws/docs/course-guide.pptx
cp ~/Downloads/ml_course_guide.pdf ~/ekd_catkin_ws/docs/course-guide.pdf
```

Move the SafeZone project overview from Downloads into the EKD docs folder with:

```bash
mv ~/Downloads/about.md ~/ekd_catkin_ws/docs/about.md
```

## EKD SafeZone YOLOv5

The original `~/yolov5` is kept unchanged. The SafeZone repository is bundled at `~/ekd_catkin_ws/ekd_yolov5`; the EKD ROS detectors use its `weights/safezone_best.pt` alias, which points relatively to the archived `analysis/sz-mod-training-2026-11-09/training/weights/best.pt`. The matching `data/sz-mod.yaml` defines `scissors` and `earbuds`.

Inspect the archive and confirm it is valid:

```bash
unzip -l "$HOME/Downloads/safezone.zip"
unzip -t "$HOME/Downloads/safezone.zip"
```

Extract it once into the EKD repository. These commands refuse to overwrite either the temporary extraction path or the final path:

```bash
if [[ -e "$HOME/ekd_catkin_ws/safezone" || -e "$HOME/ekd_catkin_ws/ekd_yolov5" ]]; then
	printf 'Refusing to overwrite an existing extraction path.\n' >&2
	exit 1
fi
unzip -q "$HOME/Downloads/safezone.zip" 'safezone/*' -d "$HOME/ekd_catkin_ws" &&
mv "$HOME/ekd_catkin_ws/safezone" "$HOME/ekd_catkin_ws/ekd_yolov5"
```

Create the short runtime alias without copying or replacing the archived checkpoint:

```bash
mkdir -p "$HOME/ekd_catkin_ws/ekd_yolov5/weights"
ln -s ../analysis/sz-mod-training-2026-11-09/training/weights/best.pt \
	"$HOME/ekd_catkin_ws/ekd_yolov5/weights/safezone_best.pt"
```

Verify the repository, SafeZone config, alias, and alias target:

```bash
test -f "$HOME/ekd_catkin_ws/ekd_yolov5/models/common.py" &&
test -f "$HOME/ekd_catkin_ws/ekd_yolov5/data/sz-mod.yaml" &&
test -L "$HOME/ekd_catkin_ws/ekd_yolov5/weights/safezone_best.pt" &&
test -f "$HOME/ekd_catkin_ws/ekd_yolov5/weights/safezone_best.pt" &&
readlink -f "$HOME/ekd_catkin_ws/ekd_yolov5/weights/safezone_best.pt"
```

Run custom inference directly from the EKD copy:

```bash
cd "$HOME/ekd_catkin_ws/ekd_yolov5"
python3 detect.py \
	--weights weights/safezone_best.pt \
	--data data/sz-mod.yaml \
	--source data/images
```

Run the EKD ROS detector with the SafeZone defaults:

```bash
source ~/ekd_catkin_ws/setup_ekd.bash
roslaunch jupiterobot2_vision_yolov5 object_detection.launch
```

The EKD detector defaults are defined in `detector.py`, `detector_cn.py`, and `detect.py` under the vision package, plus the Qt copy at `jupiterobot2_qt/scripts/yolo_scripts/detector_cn.py`. They resolve `ekd_yolov5/weights/safezone_best.pt` relative to the workspace root, so a clone contains the model code and checkpoint.

## 1) Duplicate the workspace

Original:

```bash
cp -a /home/mustar/catkin_ws /home/mustar/ekd_catkin_ws
```

Equivalent in a more compact form:

```bash
cd /home/mustar
cp -a catkin_ws ekd_catkin_ws
```

## 2) Enter the workspace

Original:

```bash
cd /home/mustar/catkin_ws
```

New:

```bash
cd /home/mustar/ekd_catkin_ws
```

## 3) Source ROS and the workspace environment

Original:

```bash
cd /home/mustar/catkin_ws
source /opt/ros/noetic/setup.bash
source /home/mustar/catkin_ws/devel/setup.bash
```

New:

```bash
cd /home/mustar/ekd_catkin_ws
source /home/mustar/ekd_catkin_ws/setup_ekd.bash
```

Run the matching setup once at the beginning of each terminal. Keep using that terminal for the selected workspace; do not source the setup again for each task. For original `catkin_ws`:

```bash
cd /home/mustar/catkin_ws
source /opt/ros/noetic/setup.bash
source devel/setup.bash
```

For EKD:

```bash
cd /home/mustar/ekd_catkin_ws
source setup_ekd.bash
```

## 4) Build the workspace

Original:

```bash
cd /home/mustar/catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make
```

New:

```bash
cd /home/mustar/ekd_catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make
```

If EKD needs a fresh build, preserve the current generated directories as backups instead of deleting them:

```bash
cd /home/mustar/ekd_catkin_ws
stamp=$(date +%Y%m%d-%H%M%S)
mv build "build.before-ekd-rebuild-$stamp"
mv devel "devel.before-ekd-rebuild-$stamp"
source /opt/ros/noetic/setup.bash
catkin_make
```

## 5) Run ROS core

Use one terminal per ROS session. Run the setup lines first, then start `roscore` in the same terminal and leave it running.

Original, Terminal 1 (run setup once in this terminal):

```bash
cd ~/catkin_ws
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
# After setup, start the ROS master.
roscore
```

EKD, Terminal 1 (run setup once in this terminal):

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
# After setup, start the ROS master.
roscore
```

## 6) Launch nodes and packages

Open a second terminal for each node or launch. Source the same workspace in each new terminal, then run one ROS command in it.

Original, Terminal 2 (new terminal; run setup once):

```bash
cd ~/catkin_ws
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
# After setup, start the selected node or launch.
roslaunch <package_name> <launch_file.launch>
```

EKD, Terminal 2 (new terminal; run setup once):

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
# After setup, start the selected node or launch.
roslaunch <package_name> <launch_file.launch>
```

Example: the original workspace uses two terminals (master and bringup launch).

```bash
cd ~/catkin_ws
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
# Terminal 1: start the master.
roscore
```

```bash
cd ~/catkin_ws
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
# Terminal 2: start the bringup launch.
roslaunch jupiterobot2_bringup bringup.launch
```

For EKD, use the same two-terminal pattern with its setup helper:

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
# Terminal 1: start the master.
roscore
```

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
# Terminal 2: start the bringup launch.
roslaunch jupiterobot2_bringup bringup.launch
```

## 7) Typical full workflow for the copied workspace

Build in Terminal 1. Run each line separately in the same terminal:

```bash
cd /home/mustar/ekd_catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make
```

For a ROS session, open Terminal 1 and set it up once, then start the master and leave it running:

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
roscore
```

Open Terminal 2, set it up once, then launch the selected package:

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
roslaunch <package_name> <launch_file.launch>
```

## 8) Important note for the copied workspace

After copying the workspace, generated build files may still contain the original path names. The EKD workspace has already been rebuilt at its own path. If another fresh build is needed, move its existing build outputs aside first as shown above; do not remove or rebuild the original workspace's directories.

The setup helper is specific to EKD and can be sourced from any working directory.

## Course guide experiments: original vs EKD

The course-guide commands are generally the same for both workspaces; the workspace you source selects which code ROS uses. In each terminal, first enter and source the selected workspace **once**. Keep using that terminal for commands in that workspace; do not repeat the setup for every task. Every newly opened terminal needs its own setup because terminal environments are separate. Do not mix the original and EKD workspaces within one terminal.

Original workspace setup, run once at the beginning of each terminal:

```bash
cd /home/mustar/catkin_ws
# Or use: cd "$HOME/catkin_ws"
source /opt/ros/noetic/setup.bash
source /home/mustar/catkin_ws/devel/setup.bash
```

Alternatively, use `$HOME` for the source path too:

```bash
cd ~/catkin_ws
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
```

EKD workspace setup, run once at the beginning of each terminal:

```bash
cd /home/mustar/ekd_catkin_ws
# Or use: cd "$HOME/ekd_catkin_ws"
source /home/mustar/ekd_catkin_ws/setup_ekd.bash
```

Alternatively, use `$HOME` for both paths:

```bash
cd ~/ekd_catkin_ws
source ~/ekd_catkin_ws/setup_ekd.bash
```

For ROS tasks, start one `roscore` and leave it running. The terminal-count notes include that master. Commands below omit the setup lines because they have already been run once in each terminal.

### Build and GUI

The guide's setup slide clones `jupiterobot2_qt`. That package is already present in both workspaces, so do not clone it again into EKD.

Build each workspace in one terminal. For EKD build, source ROS Noetic but not the EKD helper: the helper expects an existing `devel/setup.bash`. The GUI needs two terminals: Terminal 1 runs `roscore`; Terminal 2 runs the GUI.

| Operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| Build (1 terminal) | `cd ~/catkin_ws`<br>`source /opt/ros/noetic/setup.bash`<br>`catkin_make` | `cd ~/ekd_catkin_ws`<br>`source /opt/ros/noetic/setup.bash`<br>`catkin_make` |
| Demo GUI (2 terminals) | Terminal 1: `roscore`<br>Terminal 2: `roslaunch jupiterobot2_qt jupiterobot2_qt.launch` | Terminal 1: `roscore`<br>Terminal 2: `roslaunch jupiterobot2_qt jupiterobot2_qt.launch` |

### Speech and chatbot

Use three terminals for each speech or chatbot workflow: Terminal 1 runs `roscore`; Terminal 2 runs the speech/chatbot node; Terminal 3 publishes the wake, speech, or chatbot input. Each terminal should already have been initialized once for the selected workspace. The one-shot chatbot publisher exits after sending one message; wake and speech-text publishers remain active until stopped.

| Course guide operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| ROS master (Terminal 1) | `roscore` | `roscore` |
| Speech recognition node (Terminal 2) | `rosrun jupiterobot2_voice_xf iat_publish` | `rosrun jupiterobot2_voice_xf iat_publish` |
| Wake publisher (Terminal 3) | `rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` | `rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` |
| Speech synthesis node (Terminal 2) | `rosrun jupiterobot2_voice_xf tts_subscribe` | `rosrun jupiterobot2_voice_xf tts_subscribe` |
| Speech text publisher (Terminal 3) | `rostopic pub /voiceWords std_msgs/String "data: 'hello robot'"` | `rostopic pub /voiceWords std_msgs/String "data: 'hello robot'"` |
| Repeat voice launch (Terminal 2) | `roslaunch jupiterobot2_voice_xf repeat_voice.launch` | `roslaunch jupiterobot2_voice_xf repeat_voice.launch` |
| Repeat voice wake publisher (Terminal 3) | `rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` | `rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` |
| Voice assistant (Terminal 2) | `roslaunch jupiterobot2_voice_xf voice_assistant.launch` | `roslaunch jupiterobot2_voice_xf voice_assistant.launch` |
| Voice assistant wake publisher (Terminal 3) | `rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` | `rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` |
| DeepSeek chatbot (Terminal 2) | `roslaunch rfa_gpt deepseek.launch` | `roslaunch rfa_gpt deepseek.launch` |
| Qwen chatbot (Terminal 2) | `roslaunch rfa_gpt qwen.launch` | `roslaunch rfa_gpt qwen.launch` |
| Chatbot input (Terminal 3) | `rostopic pub -1 /gpt_in std_msgs/String "data: 'hello'"` | `rostopic pub -1 /gpt_in std_msgs/String "data: 'hello'"` |

Speech examples require the robot's supported speech hardware/SDK. Chatbot launches require API credentials in the private EKD environment file described below; never put credential values in this guide or the YAML files.

### EKD chatbot credentials

The EKD GPT clients read credentials from `~/ekd_catkin_ws/.env`; `setup_ekd.bash` loads that file when sourced. The root `.gitignore` excludes `.env`, and the current file is owner-readable only (`chmod 600`). Edit the local file directly with `nano ~/ekd_catkin_ws/.env` and set the variables needed by the provider:

| Client config | Environment variable |
| --- | --- |
| `config/var.yaml` | `EKD_OPENAI_API_KEY` |
| `config/qwen.yaml` | `EKD_QWEN_API_KEY` |
| SafeZone event-triggered Qwen image context | `EKD_QWEN_API_KEY` |
| `config/deepseek.yaml` | `EKD_DEEPSEEK_API_KEY` |
| Qt `qwen_ros` and DashScope VLM clients | `EKD_DASHSCOPE_API_KEY` |
| Spark speech demo | `EKD_SPARK_APP_ID`, `EKD_SPARK_API_KEY`, `EKD_SPARK_API_SECRET` |
| iFlytek TTS demos | `EKD_XFYUN_APP_ID`, `EKD_XFYUN_API_KEY`, `EKD_XFYUN_API_SECRET` |
| OpenAI VLM object detection | `EKD_OPENAI_API_KEY` |

The EKD YAML files hold only endpoint/model/prompt settings. SafeZone uses the configured RFA-compatible MAAS endpoint and `qwen3.8-max`; the existing Qt Qwen clients that still use DashScope keep their separate `EKD_DASHSCOPE_API_KEY`. DeepSeek had a placeholder rather than a real credential and remains unset; its launch will report the missing variable until a key is configured. To load changes into a terminal, source `~/ekd_catkin_ws/setup_ekd.bash` again. Do not copy the `.env` into `catkin_ws` or share its contents. Rotate any credentials that appeared in prior chat or diagnostic output before using or publishing the project.

On a new machine, start from `.env.example` with `cp .env.example .env`, set local values, and run `chmod 600 .env`. See `deployment/README.md` for the one-clone ROS Noetic setup and Git LFS steps.

### Cameras, photos, and OpenCV

Using the explicit-master workflow, camera-based viewing or detection uses three terminals: Terminal 1 runs `roscore`, Terminal 2 runs the camera launch, and Terminal 3 runs one viewer or vision command. Direct photo capture also uses three terminals. The subscriber photo exercise uses four: master, camera, subscriber, and trigger publisher. RQT without a camera uses two terminals (master and RQT); with a camera, use three.

In Terminal 2, choose the camera command matching the hardware. Then run the viewer or vision command in Terminal 3. Each terminal should already be set up once using the workspace instructions above; there is no need to source again for every command.

| Course guide operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| Jupiter 2 camera (Terminal 2) | `roslaunch jupiterobot2_bringup multi_camera.launch` | `roslaunch jupiterobot2_bringup multi_camera.launch` |
| Juno 2 Astra camera (Terminal 2) | `roslaunch astra_camera astra.launch` | `roslaunch astra_camera astra.launch` |
| RGB viewer (Terminal 3) | `rosrun image_view image_view image:=/camera/color/image_raw` | `rosrun image_view image_view image:=/camera/color/image_raw` |
| Depth viewer (Terminal 3) | `rosrun image_view image_view image:=/camera/depth/image_raw` | `rosrun image_view image_view image:=/camera/depth/image_raw` |
| RQT (Terminal 3 with camera; Terminal 2 without camera) | `rqt` | `rqt` |
| Take photo (Terminal 3) | `rosrun rchomeedu_vision take_photo.py` (as printed in the guide) | `rosrun rfa_vision take_photo.py` |
| Take photo subscriber (Terminal 3) | `rosrun rchomeedu_vision take_photo_sub.py` | `rosrun rfa_vision take_photo_sub.py` |
| Trigger photo subscriber (Terminal 4) | `rostopic pub -1 /take_photo std_msgs/String "take photo"` | `rostopic pub -1 /take_photo std_msgs/String "take photo"` |
| CamShift (Terminal 3) | `roslaunch opencv_apps camshift.launch image:=/camera/color/image_raw` | `roslaunch opencv_apps camshift.launch image:=/camera/color/image_raw` |
| Face detection (Terminal 3) | `roslaunch opencv_apps face_detection.launch image:=/camera/color/image_raw` | `roslaunch opencv_apps face_detection.launch image:=/camera/color/image_raw` |
| Face recognition (Terminal 3) | `roslaunch opencv_apps face_recognition.launch image:=/camera/color/image_raw` | `roslaunch opencv_apps face_recognition.launch image:=/camera/color/image_raw` |
| People detection (Terminal 3) | `roslaunch opencv_apps people_detect.launch image:=/camera/color/image_raw` | `roslaunch opencv_apps people_detect.launch image:=/camera/color/image_raw` |

The guide's `rchomeedu_vision` package is absent from EKD; its photo scripts are available as `rfa_vision`. For a Jupiter 2 bottom camera, replace `/camera/` with `/camera_bot/` in the image topic as the course guide notes.

### YOLO, MediaPipe, and VLM

YOLO, MediaPipe, and VLM examples use three terminals: Terminal 1 runs the ROS master, Terminal 2 the camera, and Terminal 3 the selected detector. Run one detection command at a time. These terminals should already be set up once for the selected workspace.

| Course guide operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| YOLO object detection (Terminal 3) | `roslaunch jupiterobot2_vision_yolov5 object_detection.launch` | `roslaunch jupiterobot2_vision_yolov5 object_detection.launch` |
| MediaPipe pose (Terminal 3) | `roslaunch jupiterobot2_vision_mediapipe mediapipe_pose.launch` | `roslaunch jupiterobot2_vision_mediapipe mediapipe_pose.launch` |
| MediaPipe face detection (Terminal 3) | `roslaunch jupiterobot2_vision_mediapipe mediapipe_faceDetect.launch` | `roslaunch jupiterobot2_vision_mediapipe mediapipe_faceDetect.launch` |
| MediaPipe face mesh (Terminal 3) | `roslaunch jupiterobot2_vision_mediapipe mediapipe_faceMesh.launch` | `roslaunch jupiterobot2_vision_mediapipe mediapipe_faceMesh.launch` |
| MediaPipe hand (Terminal 3) | `roslaunch jupiterobot2_vision_mediapipe mediapipe_hand.launch` | `roslaunch jupiterobot2_vision_mediapipe mediapipe_hand.launch` |
| VLM image recognition (Terminal 3) | `rosrun rfa_vlm image_recognition_qwen.py` | `rosrun rfa_vlm image_recognition_qwen.py` |
| VLM object detection (Terminal 3) | `rosrun rfa_vlm object_detection_qwen.py` | `rosrun rfa_vlm object_detection_qwen.py` |

Start the appropriate camera before camera-based vision commands. The PDF's custom YOLO training slide gives general steps and external tutorials, not a complete runnable training command; use the SafeZone dataset/config and training notes in `~/ekd_catkin_ws/ekd_yolov5/docs/README.md` instead. The photo-by-voice and publisher/subscriber items are exercises, not prebuilt single launch commands.

### EKD command validation

The following checks were run without starting hardware or inference nodes:

- `rospack find` resolved all guide packages except `rchomeedu_vision`; EKD's equivalent photo package is `rfa_vision`.
- `roslaunch --nodes` parsed the GUI, speech, chatbot, camera, OpenCV, YOLO, and MediaPipe launch files.
- `rosrun --prefix /bin/true` resolved the photo and VLM scripts; the voice binaries exist in the EKD devel space.
- The unused `Wunti` Catkin starter package was removed; it contained only the default talker/listener scaffold and had no workspace dependencies.

## 9) Quick cheat sheet

| Action | Original workspace | EKD workspace |
| --- | --- | --- |
| Enter workspace | `cd /home/mustar/catkin_ws` | `cd /home/mustar/ekd_catkin_ws` |
| Initialize environment (once per terminal) | `cd ~/catkin_ws`<br>`source /opt/ros/noetic/setup.bash`<br>`source ~/catkin_ws/devel/setup.bash` | `cd ~/ekd_catkin_ws`<br>`source ~/ekd_catkin_ws/setup_ekd.bash` |
| Build (1 terminal) | `cd ~/catkin_ws`<br>`source /opt/ros/noetic/setup.bash`<br>`catkin_make` | `cd ~/ekd_catkin_ws`<br>`source /opt/ros/noetic/setup.bash`<br>`catkin_make` |
| Fresh build | Move generated directories to timestamped backups, then run `catkin_make` | Move generated directories to timestamped backups, then run `catkin_make` |
| ROS master (Terminal 1, after setup) | `roscore` | `roscore` |
| Launch node (new terminal, after setup) | `roslaunch ...` | `roslaunch ...` |

Initialize each new terminal once using the row above, then reuse it for commands in that workspace. Do not source again for every task. Use one terminal per long-running master, camera, or node. Exact terminal counts are listed above and in the copy-and-paste reference.
