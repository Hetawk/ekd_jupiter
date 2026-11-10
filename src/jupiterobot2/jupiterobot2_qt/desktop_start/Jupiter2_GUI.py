import os

# 启动终端并执行带 source 的 roslaunch 命令
command = (
    "gnome-terminal -- bash -c \""
    "source /opt/ros/noetic/setup.bash; "
    "source ~/ekd_catkin_ws/devel/setup.bash; "
    "roslaunch jupiterobot2_qt jupiterobot2_qt.launch; "
    "exec bash\""
)

os.system(command)