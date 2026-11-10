# COURSE GUIDE COMMANDS - COPY AND PASTE BY TERMINAL
# This is a reference, not a runnable script. Do not execute or source it.
# Copy only the commands for the task/workspace you want.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
	printf 'Reference only: open this file and copy the commands by terminal.\n' >&2
	exit 2
fi

if false; then

###############################################################################
# FIRST: INITIALIZE EACH TERMINAL ONCE
# Choose ONE workspace setup below in every terminal you open for that workspace.
# The cd is included so the active workspace directory is explicit.
# Keep using that terminal for the same workspace; do not source again for every
# task. A newly opened terminal has a separate environment and needs setup once.
###############################################################################

# ORIGINAL WORKSPACE - run once in each original-workspace terminal.
# Choose ONE path form to enter the original Catkin workspace.
cd /home/mustar/catkin_ws
# Or use this instead: cd "$HOME/catkin_ws"
# Load ROS Noetic.
source /opt/ros/noetic/setup.bash
# Load the original workspace (choose either source path form).
source /home/mustar/catkin_ws/devel/setup.bash
# Or use this instead: source "$HOME/catkin_ws/devel/setup.bash"

# EKD WORKSPACE - run once in each EKD terminal instead of the original lines.
# Choose ONE path form to enter the modified EKD Catkin workspace.
cd /home/mustar/ekd_catkin_ws
# Or use this instead: cd "$HOME/ekd_catkin_ws"
# Load ROS Noetic, the EKD workspace, and its local environment (choose either path).
source /home/mustar/ekd_catkin_ws/setup_ekd.bash
# Or use this instead: source "$HOME/ekd_catkin_ws/setup_ekd.bash"

# BUILDING (different setup): run in one terminal per workspace.
# For a build, use the workspace path and ROS Noetic only; do not source the
# workspace's devel setup first.
# Original build terminal:
cd /home/mustar/catkin_ws
# Or use this instead: cd "$HOME/catkin_ws"
source /opt/ros/noetic/setup.bash
catkin_make
# EKD build terminal:
cd /home/mustar/ekd_catkin_ws
# Or use this instead: cd "$HOME/ekd_catkin_ws"
source /opt/ros/noetic/setup.bash
catkin_make

###############################################################################
# COURSE DEMO GUI
# 2 terminals per run: Terminal 1 = ROS master; Terminal 2 = GUI.
# First initialize each terminal once using the chosen workspace setup above.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2: start the course demo GUI.
roslaunch jupiterobot2_qt jupiterobot2_qt.launch

###############################################################################
# SPEECH RECOGNITION
# 3 terminals: Terminal 1 = ROS master; Terminal 2 = recognition node;
# Terminal 3 = wake publisher. Requires supported speech hardware/SDK.
# Initialize each terminal once using the same workspace setup.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2: run speech recognition.
rosrun jupiterobot2_voice_xf iat_publish
# Terminal 3: send the wake message.
rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"

###############################################################################
# SPEECH SYNTHESIS
# 3 terminals: Terminal 1 = ROS master; Terminal 2 = speech listener;
# Terminal 3 = text publisher. Requires supported speech hardware/SDK.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2: listen for speech text.
rosrun jupiterobot2_voice_xf tts_subscribe
# Terminal 3: publish text for the robot to speak.
rostopic pub /voiceWords std_msgs/String "data: 'hello robot'"

###############################################################################
# REPEAT-VOICE DEMO
# 3 terminals: Terminal 1 = ROS master; Terminal 2 = repeat-voice launch;
# Terminal 3 = wake publisher. Requires supported speech hardware/SDK.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2: launch the repeat-voice demo.
roslaunch jupiterobot2_voice_xf repeat_voice.launch
# Terminal 3: publish the wake message.
rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"

###############################################################################
# VOICE ASSISTANT
# 3 terminals: Terminal 1 = ROS master; Terminal 2 = voice assistant;
# Terminal 3 = wake publisher. Requires supported speech hardware/SDK.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2: launch the voice assistant.
roslaunch jupiterobot2_voice_xf voice_assistant.launch
# Terminal 3: publish the wake message.
rostopic pub /voiceWakeup std_msgs/String "data: 'any string'"

###############################################################################
# DEEPSEEK OR QWEN CHATBOT
# 3 terminals: Terminal 1 = ROS master; Terminal 2 = one chatbot launch;
# Terminal 3 = input publisher. EKD credentials must be configured for EKD.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2: choose ONE chatbot launch.
roslaunch rfa_gpt deepseek.launch
# Or, instead of DeepSeek, launch Qwen in Terminal 2.
roslaunch rfa_gpt qwen.launch
# Terminal 3: send one prompt to the running chatbot.
rostopic pub -1 /gpt_in std_msgs/String "data: 'hello'"

###############################################################################
# CAMERA SETUP
# 2 terminals for the master and camera; use a third for a viewer or detector.
# Use the appropriate camera for your hardware. Choose one camera command.
###############################################################################
# Terminal 1: start the ROS master and leave it running.
roscore
# Terminal 2, Jupiter 2: bring up the robot cameras.
roslaunch jupiterobot2_bringup multi_camera.launch
# Instead of the Jupiter 2 command, Terminal 2, Juno 2: bring up Astra.
roslaunch astra_camera astra.launch

###############################################################################
# CAMERA VIEWERS AND VISION
# 3 terminals total: master, camera, and one selected viewer/detector.
# Initialize each terminal once. Run only one viewer/detector at a time.
# For Jupiter 2 bottom camera, change /camera/ to /camera_bot/ in the topic.
###############################################################################
# Terminal 3: display RGB images.
rosrun image_view image_view image:=/camera/color/image_raw
# Terminal 3: display depth images.
rosrun image_view image_view image:=/camera/depth/image_raw
# Terminal 3: open RQT (without a camera, use 2 terminals: master and RQT).
rqt
# Terminal 3: run OpenCV CamShift tracking.
roslaunch opencv_apps camshift.launch image:=/camera/color/image_raw
# Terminal 3: run OpenCV face detection.
roslaunch opencv_apps face_detection.launch image:=/camera/color/image_raw
# Terminal 3: run OpenCV face recognition.
roslaunch opencv_apps face_recognition.launch image:=/camera/color/image_raw
# Terminal 3: run OpenCV people detection.
roslaunch opencv_apps people_detect.launch image:=/camera/color/image_raw
# Terminal 3: run YOLO object detection.
roslaunch jupiterobot2_vision_yolov5 object_detection.launch
# Terminal 3: run MediaPipe pose estimation.
roslaunch jupiterobot2_vision_mediapipe mediapipe_pose.launch
# Terminal 3: run MediaPipe face detection.
roslaunch jupiterobot2_vision_mediapipe mediapipe_faceDetect.launch
# Terminal 3: run MediaPipe face mesh.
roslaunch jupiterobot2_vision_mediapipe mediapipe_faceMesh.launch
# Terminal 3: run MediaPipe hand landmarks.
roslaunch jupiterobot2_vision_mediapipe mediapipe_hand.launch
# Terminal 3: run Qwen VLM image recognition.
rosrun rfa_vlm image_recognition_qwen.py
# Terminal 3: run Qwen VLM object detection.
rosrun rfa_vlm object_detection_qwen.py

###############################################################################
# DIRECT PHOTO CAPTURE
# 3 terminals: ROS master, camera, and photo command. Initialize each once.
###############################################################################
# Terminal 1: start the ROS master.
roscore
# Terminal 2: start one camera using the commands in CAMERA SETUP above.
# Terminal 3, original workspace: capture a photo.
rosrun rchomeedu_vision take_photo.py
# Terminal 3, EKD workspace: capture a photo (EKD package is rfa_vision).
rosrun rfa_vision take_photo.py

###############################################################################
# PHOTO SUBSCRIBER EXERCISE
# 4 terminals: ROS master, camera, subscriber, and trigger publisher.
###############################################################################
# Terminal 1: start the ROS master.
roscore
# Terminal 2: start one camera using the commands in CAMERA SETUP above.
# Terminal 3, original workspace: start the photo subscriber.
rosrun rchomeedu_vision take_photo_sub.py
# Terminal 3, EKD workspace: start the photo subscriber (package is rfa_vision).
rosrun rfa_vision take_photo_sub.py
# Terminal 4: trigger the subscriber once.
rostopic pub -1 /take_photo std_msgs/String "take photo"

###############################################################################
# END OF COPY-AND-PASTE REFERENCE
###############################################################################
fi
