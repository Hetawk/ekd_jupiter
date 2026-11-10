#!/bin/bash
source /opt/ros/noetic/setup.bash
source /home/mustar/ekd_catkin_ws/devel/setup.bash
terminator -e "roslaunch jupiterobot2_qt jupiterobot2_qt.launch"


# /bin/bash -c "/home/mustar/ekd_catkin_ws/src/jupiterobot2_qt/jupiterobot2_qt/launch_qt.sh"