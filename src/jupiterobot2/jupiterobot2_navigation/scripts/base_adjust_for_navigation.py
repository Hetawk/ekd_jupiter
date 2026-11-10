#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023 Jupiter Robot Technology Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Dante Huang

import rospy
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped

def main():
    # 初始化 Twist 控制消息
    twist = Twist()
    twist.linear.x = 0
    twist.linear.y = 0
    twist.linear.z = 0
    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0.5

    # 初始化 ros 节点
    rospy.init_node("base_adj_for_nav", disable_signals=True)

    # 初始化控制命令发布者
    pub = rospy.Publisher("cmd_vel", Twist, queue_size=1)

    # 等待用户指定机器人初始位置
    rospy.loginfo("\033[40;32;1m"+"Please click the 2D Pose Estimate button in RViz to set the robot's initial pose..."+"\033[0m")
    rospy.wait_for_message('initialpose', PoseWithCovarianceStamped)
    rospy.sleep(2)

    # 发布命令让底盘先转一圈
    rate = rospy.Rate(10)
    t = 0
    while(t < 140):
        pub.publish(twist)
        t += 1
        rate.sleep()
    # 停稳扶好
    pub.publish(Twist())
    rospy.sleep(1)

    # 关闭节点
    rospy.loginfo("\033[32;1m"+"Scanning completed."+"\033[0m")
    rospy.signal_shutdown("Scanning completed.")


if __name__ == "__main__":
    main()

