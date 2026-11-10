# ROS workspace command guide

This file records the commands normally used for the original workspace and the matching commands to use in the duplicated workspace.

## Recommended EKD workflow

The original workspace remains the default in `~/.bashrc`. To select EKD in the current terminal without changing that default, source its helper:

```bash
source ~/ekd_catkin_ws/setup_ekd.bash
```

This sources ROS Noetic and the EKD devel environment, and sets `EKD_CATKIN_WS`. It does not modify `~/.bashrc` or the original `catkin_ws`.

Build EKD with:

```bash
cd "$EKD_CATKIN_WS"
catkin_make
```

In each new terminal used for EKD, source the helper before running `roslaunch`, `rosrun`, or other ROS commands:

```bash
source ~/ekd_catkin_ws/setup_ekd.bash
roslaunch <package_name> <launch_file.launch>
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
source /opt/ros/noetic/setup.bash
source /home/mustar/catkin_ws/devel/setup.bash
```

New:

```bash
source /home/mustar/ekd_catkin_ws/setup_ekd.bash
```

If you prefer a shorter pattern, a common setup is:

```bash
cd /home/mustar/catkin_ws
source /opt/ros/noetic/setup.bash
source devel/setup.bash
```

And for the copied workspace:

```bash
cd /home/mustar/ekd_catkin_ws
source /opt/ros/noetic/setup.bash
source devel/setup.bash
```

## 4) Build the workspace

Original:

```bash
cd /home/mustar/catkin_ws
catkin_make
```

New:

```bash
cd /home/mustar/ekd_catkin_ws
source setup_ekd.bash
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

Original:

```bash
roscore
```

New:

```bash
roscore
```

The command is the same; only the workspace path changes when you source it.

## 6) Launch nodes and packages

Original:

```bash
roslaunch <package_name> <launch_file.launch>
```

New:

```bash
roslaunch <package_name> <launch_file.launch>
```

Example pattern:

```bash
cd /home/mustar/catkin_ws
source devel/setup.bash
roslaunch jupiterobot2_bringup bringup.launch
```

```bash
cd /home/mustar/ekd_catkin_ws
source devel/setup.bash
roslaunch jupiterobot2_bringup bringup.launch
```

## 7) Typical full workflow for the copied workspace

```bash
cd /home/mustar/ekd_catkin_ws
source setup_ekd.bash
catkin_make
roscore
```

Then in another terminal:

```bash
source ~/ekd_catkin_ws/setup_ekd.bash
roslaunch <package_name> <launch_file.launch>
```

## 8) Important note for the copied workspace

After copying the workspace, generated build files may still contain the original path names. The EKD workspace has already been rebuilt at its own path. If another fresh build is needed, move its existing build outputs aside first as shown above; do not remove or rebuild the original workspace's directories.

The setup helper is specific to EKD and can be sourced from any working directory.

## Course guide experiments: original vs EKD

The course guide's ROS operation commands are the same in both workspaces; the sourced workspace selects which code ROS uses. Run the matching setup command in every terminal before its ROS command:

| Original workspace setup | EKD workspace setup |
| --- | --- |
| `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash` | `source ~/ekd_catkin_ws/setup_ekd.bash` |

Start `roscore` once per ROS session. Run each node or launch in a separate terminal as needed, and source that terminal for the workspace you intend to use.

### Build and GUI

The guide's setup slide clones `jupiterobot2_qt`. That package is already present in both workspaces, so do not clone it again into EKD.

| Operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| Build | `cd ~/catkin_ws && source /opt/ros/noetic/setup.bash && catkin_make` | `cd ~/ekd_catkin_ws && source /opt/ros/noetic/setup.bash && catkin_make` |
| Demo GUI | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch jupiterobot2_qt jupiterobot2_qt.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_qt jupiterobot2_qt.launch` |

### Speech and chatbot

| Course guide operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| ROS master | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roscore` | `source ~/ekd_catkin_ws/setup_ekd.bash && roscore` |
| Speech recognition node | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rosrun jupiterobot2_voice_xf iat_publish` | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun jupiterobot2_voice_xf iat_publish` |
| Wake speech node | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` | `source ~/ekd_catkin_ws/setup_ekd.bash && rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"` |
| Speech synthesis node | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rosrun jupiterobot2_voice_xf tts_subscribe` | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun jupiterobot2_voice_xf tts_subscribe` |
| Send speech text | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rostopic pub /voiceWords std_msgs/String "data: 'hello robot'"` | `source ~/ekd_catkin_ws/setup_ekd.bash && rostopic pub /voiceWords std_msgs/String "data: 'hello robot'"` |
| Repeat voice launch | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch jupiterobot2_voice_xf repeat_voice.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_voice_xf repeat_voice.launch` |
| Voice assistant | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch jupiterobot2_voice_xf voice_assistant.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_voice_xf voice_assistant.launch` |
| DeepSeek chatbot | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rfa_gpt deepseek.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch rfa_gpt deepseek.launch` |
| Qwen chatbot | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rfa_gpt qwen.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch rfa_gpt qwen.launch` |
| Send chatbot input | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rostopic pub -1 /gpt_in std_msgs/String "data: 'hello'"` | `source ~/ekd_catkin_ws/setup_ekd.bash && rostopic pub -1 /gpt_in std_msgs/String "data: 'hello'"` |

Speech examples require the robot's supported speech hardware/SDK. Chatbot launches require API credentials in the private EKD environment file described below; never put credential values in this guide or the YAML files.

### EKD chatbot credentials

The EKD GPT clients read credentials from `~/ekd_catkin_ws/.env`; `setup_ekd.bash` loads that file when sourced. The root `.gitignore` excludes `.env`, and the current file is owner-readable only (`chmod 600`). Edit the local file directly with `nano ~/ekd_catkin_ws/.env` and set the variables needed by the provider:

| Client config | Environment variable |
| --- | --- |
| `config/var.yaml` | `EKD_OPENAI_API_KEY` |
| `config/qwen.yaml` | `EKD_QWEN_API_KEY` |
| `config/deepseek.yaml` | `EKD_DEEPSEEK_API_KEY` |
| Qt `qwen_ros` and DashScope VLM clients | `EKD_DASHSCOPE_API_KEY` |
| Spark speech demo | `EKD_SPARK_APP_ID`, `EKD_SPARK_API_KEY`, `EKD_SPARK_API_SECRET` |
| iFlytek TTS demos | `EKD_XFYUN_APP_ID`, `EKD_XFYUN_API_KEY`, `EKD_XFYUN_API_SECRET` |
| OpenAI VLM object detection | `EKD_OPENAI_API_KEY` |

The EKD YAML files hold only endpoint/model/prompt settings. The EKD Qwen clients use separate keys for the DashScope and RFA-compatible endpoints. DeepSeek had a placeholder rather than a real credential and remains unset; its launch will report the missing variable until a key is configured. To load changes into a terminal, source `~/ekd_catkin_ws/setup_ekd.bash` again. Do not copy the `.env` into `catkin_ws` or share its contents. Rotate any credentials that appeared in prior chat or diagnostic output before using or publishing the project.

On a new machine, start from `.env.example` with `cp .env.example .env`, set local values, and run `chmod 600 .env`. See `deployment/README.md` for the one-clone ROS Noetic setup and Git LFS steps.

### Cameras, photos, and OpenCV

Use the camera command matching the hardware. Start the camera in one terminal, then the viewer or vision node in another.

| Course guide operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| Jupiter 2 camera | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup multi_camera.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_bringup multi_camera.launch` |
| Juno 2 Astra camera | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch astra_camera astra.launch` |
| RGB viewer | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rosrun image_view image_view image:=/camera/color/image_raw` | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun image_view image_view image:=/camera/color/image_raw` |
| Depth viewer | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rosrun image_view image_view image:=/camera/depth/image_raw` | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun image_view image_view image:=/camera/depth/image_raw` |
| RQT | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && rqt` | `source ~/ekd_catkin_ws/setup_ekd.bash && rqt` |
| Take photo | `rosrun rchomeedu_vision take_photo.py` (as printed in the guide) | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun rfa_vision take_photo.py` |
| Take photo subscriber | `rosrun rchomeedu_vision take_photo_sub.py` (as printed in the guide) | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun rfa_vision take_photo_sub.py` |
| Trigger photo subscriber | `rostopic pub -1 /take_photo std_msgs/String "take photo"` | `source ~/ekd_catkin_ws/setup_ekd.bash && rostopic pub -1 /take_photo std_msgs/String "take photo"` |
| CamShift | `roslaunch opencv_apps camshift.launch image:=/camera/color/image_raw` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch opencv_apps camshift.launch image:=/camera/color/image_raw` |
| Face detection | `roslaunch opencv_apps face_detection.launch image:=/camera/color/image_raw` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch opencv_apps face_detection.launch image:=/camera/color/image_raw` |
| Face recognition | `roslaunch opencv_apps face_recognition.launch image:=/camera/color/image_raw` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch opencv_apps face_recognition.launch image:=/camera/color/image_raw` |
| People detection | `roslaunch opencv_apps people_detect.launch image:=/camera/color/image_raw` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch opencv_apps people_detect.launch image:=/camera/color/image_raw` |

The guide's `rchomeedu_vision` package is absent from EKD; its photo scripts are available as `rfa_vision`. For a Jupiter 2 bottom camera, replace `/camera/` with `/camera_bot/` in the image topic as the course guide notes.

### YOLO, MediaPipe, and VLM

| Course guide operation | Original `catkin_ws` command | EKD command |
| --- | --- | --- |
| YOLO object detection | `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch jupiterobot2_vision_yolov5 object_detection.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_vision_yolov5 object_detection.launch` |
| MediaPipe pose | `roslaunch jupiterobot2_vision_mediapipe mediapipe_pose.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_pose.launch` |
| MediaPipe face detection | `roslaunch jupiterobot2_vision_mediapipe mediapipe_faceDetect.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_faceDetect.launch` |
| MediaPipe face mesh | `roslaunch jupiterobot2_vision_mediapipe mediapipe_faceMesh.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_faceMesh.launch` |
| MediaPipe hand | `roslaunch jupiterobot2_vision_mediapipe mediapipe_hand.launch` | `source ~/ekd_catkin_ws/setup_ekd.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_hand.launch` |
| VLM image recognition | `rosrun rfa_vlm image_recognition_qwen.py` | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun rfa_vlm image_recognition_qwen.py` |
| VLM object detection | `rosrun rfa_vlm object_detection_qwen.py` | `source ~/ekd_catkin_ws/setup_ekd.bash && rosrun rfa_vlm object_detection_qwen.py` |

Start the appropriate camera before camera-based vision commands. The PDF's custom YOLO training slide gives general steps and external tutorials, not a complete runnable training command; use the SafeZone dataset/config and training notes in `~/ekd_catkin_ws/ekd_yolov5/docs/README.md` instead. The photo-by-voice and publisher/subscriber items are exercises, not prebuilt single launch commands.

### EKD command validation

The following checks were run without starting hardware or inference nodes:

- `rospack find` resolved all guide packages except `rchomeedu_vision`; EKD's equivalent photo package is `rfa_vision`.
- `roslaunch --nodes` parsed the GUI, speech, chatbot, camera, OpenCV, YOLO, and MediaPipe launch files.
- `rosrun --prefix /bin/true` resolved the photo and VLM scripts; the voice binaries exist in the EKD devel space.
- The launch parser reports the existing `Wunti` package-name convention warning; it did not prevent launch-file parsing.

## 9) Quick cheat sheet

| Action | Original workspace | New workspace |
| --- | --- | --- |
| Enter workspace | `cd /home/mustar/catkin_ws` | `cd /home/mustar/ekd_catkin_ws` |
| Source ROS | `source /opt/ros/noetic/setup.bash` | `source /opt/ros/noetic/setup.bash` |
| Source workspace | `source devel/setup.bash` | `source devel/setup.bash` |
| Build | `catkin_make` | `catkin_make` |
| Fresh build | Move generated directories to timestamped backups, then run `catkin_make` | Move generated directories to timestamped backups, then run `catkin_make` |
| Run ROS | `roscore` | `roscore` |
| Launch nodes | `roslaunch ...` | `roslaunch ...` |

For EKD, source `~/ekd_catkin_ws/setup_ekd.bash` to select the duplicated workspace in the current terminal.
