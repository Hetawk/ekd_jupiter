# SafeZone Core Startup Map

## Choose workspace

**Course sample**

Command: `cd ~/catkin_ws`, then source ROS Noetic and `~/catkin_ws/devel/setup.bash`.

Command list: [ekd_catkin_ws/docs/course-guide-commands.sh](course-guide-commands.sh).

**Modified SafeZone**

Command: `cd ~/ekd_catkin_ws/docs && ./safezone.sh`

The script sources [ekd_catkin_ws/setup_ekd.bash](../setup_ekd.bash), then launches `safezone_demo.launch`.

Use one workspace per terminal. SafeZone files are EKD additions; the TTS node is reused from the course sample.

## Processes

No ROS master running: **8 PIDs start; 7 remain after cleanup exits.**

1. **`roslaunch` parent**

  Purpose: runs the SafeZone launch.

  Path: `ekd_catkin_ws/docs/safezone.sh` -> `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/launch/safezone_demo.launch`

2. **ROS master (`rosmaster`)**

  Purpose: connects ROS nodes and topics; auto-started if absent.

  Path: installed ROS Noetic under `/opt/ros/noetic`.

3. **`rosout`**

  Purpose: ROS logging node; auto-started with ROS core.

  Path: installed ROS Noetic under `/opt/ros/noetic`.

4. **`/camera/camera`**

  Purpose: publishes RGB camera images.

  Source: `ekd_catkin_ws/src/basic_function_packages/ros_astra_camera/src/main.cpp`

  Build target: `ekd_catkin_ws/src/basic_function_packages/ros_astra_camera/CMakeLists.txt`

5. **`safezone_wake`**

  Purpose: microphone input and wake phrase detection.

  Source: `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/safezone_wake.py`

6. **`safezone_assistant`**

  Purpose: detection, wake-triggered capture, policy response, and event logging.

  Source: `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/safezone_assistant.py`

7. **`safezone_tts`**

  Purpose: synthesizes and plays `/voiceWords` text.

  Source: `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_voice/jupiterobot2_voice_xf/src/tts_subscribe.cpp`

  Build target: `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_voice/jupiterobot2_voice_xf/CMakeLists.txt`

8. **`camera_shm_cleanup`** (exits after startup)

  Purpose: clears camera shared memory.

  Source: `ekd_catkin_ws/src/basic_function_packages/ros_astra_camera/src/astra_cleanup_shm_node.cpp`

  Build target: `ekd_catkin_ws/src/basic_function_packages/ros_astra_camera/CMakeLists.txt`

If a ROS master is already running, this launch starts **6 PIDs**: `roslaunch`, four long-running application nodes, and cleanup. Cleanup exits; the other five spawned processes remain.

## YOLO detection

Camera frames are passed by `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/safezone_assistant.py` to `Detector`.

Detector implementation: `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/detector.py`.

YOLOv5 model code: `ekd_catkin_ws/ekd_yolov5/models/common.py` and `ekd_catkin_ws/ekd_yolov5/utils/`.

Checkpoint used: `ekd_catkin_ws/ekd_yolov5/weights/safezone_best.pt`, an alias to `ekd_catkin_ws/ekd_yolov5/analysis/sz-mod-training-2026-11-09/training/weights/best.pt`.

SafeZone uses this local model to detect `scissors` and `earbuds`; `safezone_assistant.py` checks that both classes exist in the checkpoint.

Dataset class definition: `ekd_catkin_ws/ekd_yolov5/datasets/sz-mod/data.yaml`.

`ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/detector.py` also specifies `ekd_catkin_ws/ekd_yolov5/data/sz-mod.yaml` as its default data argument. That file is not present in the current workspace tree. PyTorch `.pt` inference gets class names from the checkpoint, so this missing YAML does not prevent the model from running.

## API key use

SafeZone's optional Qwen scene context reads `EKD_QWEN_API_KEY` in `ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/safezone_assistant.py`.

The key is loaded from the local `.env` by `ekd_catkin_ws/setup_ekd.bash`. Without it, local YOLO detection continues and SafeZone uses its built-in response.

Other API-key lookup files:

- `ekd_catkin_ws/src/rfa-speech/rfa_gpt/scripts/qwen_call.py`
- `ekd_catkin_ws/src/rfa-speech/rfa_gpt/scripts/gpt_call.py`
- `ekd_catkin_ws/src/rfa-speech/rfa_gpt/scripts/deepseek_call.py`
- `ekd_catkin_ws/src/rfa-vision/rfa_vlm/scripts/image_recognition.py`
- `ekd_catkin_ws/src/rfa-vision/rfa_vlm/scripts/image_recognition_qwen.py`
- `ekd_catkin_ws/src/rfa-vision/rfa_vlm/scripts/object_detection.py`

## Startup chain

```text
User runs ekd_catkin_ws/docs/safezone.sh
  -> source ekd_catkin_ws/setup_ekd.bash
     -> source /opt/ros/noetic/setup.bash
     -> source workspace devel/setup.bash
     -> source workspace .env, if present
     -> export EKD_CATKIN_WS
  -> roslaunch jupiterobot2_vision_yolov5 safezone_demo.launch
     -> start ROS master and rosout if no master is running
      -> start four long-running application nodes and one short-lived cleanup node
```

## ROS topic flow

```text
Camera node
  -> /camera/color/image_raw
  -> safezone_assistant

Microphone -> GStreamer -> PocketSphinx in safezone_wake
  -> /safezone/wake
  -> safezone_assistant

safezone_assistant
  -> /safezone/response  (response/status stream)
  -> /voiceWords         (spoken text)
  -> safezone_tts subscribes to voiceWords
```

Launch definition and ROS parameters:

`ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/launch/safezone_demo.launch`

Speech text publisher:

`ekd_catkin_ws/src/jupiterobot2/jupiterobot2_vision/jupiterobot2_vision_yolov5/scripts/safezone_assistant.py` publishes `/voiceWords`.

The course and EKD TTS subscribers both listen on `/voiceWords`.

Course command list: [ekd_catkin_ws/docs/course-guide-commands.sh](course-guide-commands.sh).

## Audio diagnostic note

`tts_sample.wav` was 44 bytes (WAV header only): check the TTS node output for `MSPLogin`, `QTTSSessionBegin`, `QTTSAudioGet`, or `text_to_speech` errors.
