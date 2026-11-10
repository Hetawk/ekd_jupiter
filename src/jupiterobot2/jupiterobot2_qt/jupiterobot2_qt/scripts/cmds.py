import os
import time

def stop_ros_node(process_name):
    # os.system(f"pkill -f {process_name}")
    os.system(f"rosnode kill {process_name} > /dev/null 2>&1 &")
# Ros1------------------------------------------------------------------------------------------------------------------------
# 2.2中文语音识别
def yysb_c():
    os.system(f"gnome-terminal -- bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roscore;\"")
    time.sleep(1)
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rosrun jupiterobot2_voice_xf iat_publish'
    os.system(f'gnome-terminal --tab -- bash -c "{cmd1}; exec bash"')
def wakeup():
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /voiceWakeup std_msgs/String "data: ``"'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
# 3.2启动机械臂调试程序
def varm_try():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_arm_bringup arm.launch;\"'")
def try1():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /arm1_joint/command std_msgs/Float64 -- 0.3;\"'")
def try2():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /arm2_joint/command std_msgs/Float64 -- 0.3;\"'")
def try3():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /arm3_joint/command std_msgs/Float64 -- 0.3;\"'")
def try4():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /arm4_joint/command std_msgs/Float64 -- 0.3;\"'")
def try5():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /gripper_joint/command std_msgs/Float64 -- 0.2;\"'")
def try6():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_arm_bringup arm.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /head_joint/command std_msgs/Float64 -- 0.2'
    cmd3 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /head_joint/command std_msgs/Float64 -- 0.0'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    time.sleep(2)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
    time.sleep(2)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd3};\"'")
# 3.3MoveIt 机械臂控制
def varm():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup jupiterobot2_bringup.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_arm_bringup arm.launch'
    cmd3 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup moveit_bringup.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd3};\"'")

def sim_arm():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_gazebo jupiterobot2_world.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup moveit_bringup.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")

def launch_camera():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
# 4.1目标跟踪
def img_follow():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")

    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch opencv_apps camshift.launch image:=/camera/color/image_raw'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")

# 4.5Yolo物体识别
def yolo_1():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rosrun jupiterobot2_vision_yolov5 object_detection.py'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")

# 4.2人脸检测
def face_jc():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch opencv_apps face_detection.launch image:=/camera/color/image_raw'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")

def inter_face():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_vision_openvino interactive_face.launch'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端

# 4.2人脸识别
def face_sb():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch opencv_apps face_recognition.launch image:=/camera/color/image_raw'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
# 4.6Mediapipe 识别
def med_1():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_faceDetect.launch'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
def med_2():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_hand.launch'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
def med_3():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_faceMesh.launch'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
def med_4():
    stop_ros_node("/camshift")
    stop_ros_node("/face_detection")
    stop_ros_node("/object_detection")
    stop_ros_node("/mediapipe_demo")
    stop_ros_node("/interactive_face")
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch astra_camera astra.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_vision_mediapipe mediapipe_pose.launch'
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    # time.sleep(1)
    os.system(f"bash -c '{cmd2}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")

# 5.1建立地图
def mk_map_1():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup jupiterobot2_bringup.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_navigation jupiterobot2_slam.launch'
    cmd3 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_teleop keyboard_teleop.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd3};\"'")
def save_mp():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rosrun map_server map_saver -f /home/mustar/ekd_catkin_ws/maps/test1;\"'")
# 键盘控制
def key_ctrl():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_teleop keyboard_teleop.launch;\"'")

# 5.2用 Rviz 室内导航
def rviz_1():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup jupiterobot2_bringup.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_navigation jupiterobot2_navigation.launch map_file:=/home/mustar/ekd_catkin_ws/maps/test1.yaml'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};\"'")


# 仿真建图
def sim_map():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_gazebo jupiterobot2_world.launch world_file:=/home/mustar/ekd_catkin_ws/worlds/Jupiter_Robot_Office.world'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_navigation jupiterobot2_slam.launch'
    cmd3 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_teleop keyboard_teleop.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};exec bash\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};exec bash\"' --tab -e 'bash -c \"{cmd3}; exec bash\"'")
# 保存地图
def sim_save():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rosrun map_server map_saver -f /home/mustar/ekd_catkin_ws/maps/test2;\"'")

# 6.2仿真导航
def sim_nav():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_gazebo jupiterobot2_world.launch world_file:=/home/mustar/ekd_catkin_ws/worlds/Jupiter_Robot_Office.world'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_navigation jupiterobot2_navigation.launch map_file:=/home/mustar/ekd_catkin_ws/maps/test2.yaml'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};exec bash\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};exec bash\"'")

# 6.3坐标指定机器人位置
def posi():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_gazebo jupiterobot2_world.launch world_file:=/home/mustar/ekd_catkin_ws/worlds/Jupiter_Robot_Office.world'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_navigation jupiterobot2_navigation.launch map_file:=/home/mustar/ekd_catkin_ws/maps/JupiterOfficeSim.yaml'
    cmd3 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rosrun jupiterobot2_move_grasp navigation_node.py'
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd1};exec bash\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \"{cmd2};exec bash\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd3};exec bash\"'")
def goA():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'A'\"'")
def goB():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'B'\"'")
def goC():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'C'\"'")
def goD():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'D'\"'")
def goE():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'E'\"'")
def goF():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'F'\"'")
def goG():
    os.system("gnome-terminal --window -e 'bash -c \"source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /nav_cmd std_msgs/String 'G'\"'")


def vosk():
    os.system(f"gnome-terminal --window -e 'bash -c \" source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch vosk_iat vosk_iat.launch;\"'")

def qwen():
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    os.system(f"gnome-terminal --window -e 'bash -c \" source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch qwen_ros qwen.launch;\"'")

def qwen_in():
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /qwen_Wakeup std_msgs/String "data: ``"'
    os.system(f"bash -c '{cmd2}' &")
    # os.system(f"gnome-terminal --window -e 'bash -c \" {cmd2}; \"'")

def qwen_img_in():
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && rostopic pub -1 /qwen_img_Wakeup std_msgs/String "data: ``"'
    os.system(f"bash -c '{cmd2}' &")
    # os.system(f"gnome-terminal --window -e 'bash -c \" {cmd2}; \"'")

def qwen_img():
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch qwen_ros qwen_img.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd1}; \"'")

# 7.1手势拍照
def handpic():
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'roslaunch jupiterobot2_qt gesture_photograph.launch'
    os.system(f"bash -c '{cmd1}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \" {cmd1};\"'")

# 姿态控制小海龟
def pose_turtle():
    cmd0 = 'pkill gnome-terminal'
    # os.system(f"gnome-terminal -- bash -c \"{cmd0}; exit\"")
    cmd1 = 'roslaunch pose_control_turtle pose_control_turtle.launch'
    os.system(f"bash -c '{cmd1}' &")  # 无终端
    # os.system(f"gnome-terminal --window -e 'bash -c \" {cmd1};\"'")

def run_hand_slice():
    cmd1 = 'rosrun hand_slice_game hand_slice_game.py'
    os.system(f"bash -c '{cmd1}' &")  # 无终端

def run_jump_bird():
    cmd1 = 'rosrun jupiterobot2_gesture_game pose_jump_game.py'
    os.system(f"bash -c '{cmd1}' &")  # 无终端


# 7.4follow
def followu():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup jupiterobot2_bringup.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_follower follower.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd1};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd2};\"'")

# 7.5服务生
def server():
    cmd1 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_bringup jupiterobot2_bringup.launch'
    cmd2 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_arm_bringup arm.launch'
    cmd3 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_follower follower.launch'
    cmd4 = 'source /opt/ros/noetic/setup.bash && source ~/ekd_catkin_ws/devel/setup.bash && roslaunch jupiterobot2_partybot partybot.launch'
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd1};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd2};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd3};\"'")
    time.sleep(1)
    os.system(f"gnome-terminal --window -e 'bash -c \" {cmd4};\"'")