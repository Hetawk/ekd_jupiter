#!/usr/bin/env python3
#coding=utf-8

'''
roslaunch astra_camera astra.launch
roslaunch robot_vision_openvino openpose_ros.launch
'''

import rospy
import random
from jupiterobot2_msgs.msg import Mediapipe_Pose
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn,SpawnRequest,SpawnResponse
from std_srvs.srv import Empty
import math
import time


class hand_turtle(object):
    def __init__(self):
        rospy.init_node('pose_control_turtle')
        rospy.Subscriber('/turtle1/pose', Pose, self.turtle_twords, queue_size=1)
        self.turtle_move = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=1)
        rospy.Subscriber('/mediapipe/pose', Mediapipe_Pose, self.move, queue_size=1)
        self.movemsg = Twist()

        self.client = rospy.ServiceProxy("/spawn",Spawn)
        self.clear = rospy.ServiceProxy("/clear",Empty)
        self.client.wait_for_service()
        self.last_color_change_time = time.time()

        self.req = SpawnRequest()
        self.req.x = 1.0
        self.req.y = 1.0
        self.req.theta = 3.14
        self.num=2
        self.alllow=1

        rospy.spin()


    def turtle_twords(self, msg):
        self.twords = msg.theta
        # print(self.twords)
    def move(self, msg):
        RElbow_x = msg.right_elbow.x
        RElbow_y = msg.right_elbow.y
        LElbow_y = msg.left_elbow.y
        RWrist_x = msg.right_wrist.x
        RWrist_y = msg.right_wrist.y
        LWrist_y = msg.left_wrist.y
        RShoulder_y = msg.right_shoulder.y
        LShoulder_y = msg.left_shoulder.y
        # print("RElbow_y", RElbow_y)
        # print("RWrist_y", RWrist_y)

        if LWrist_y < 480 and LShoulder_y < 480:
            if LElbow_y<LShoulder_y:
                if self.alllow==1:
                    self.req.name = "turtle" + str(self.num)
                    self.response = self.client.call(self.req)
                    self.alllow=0

        if RElbow_y < RShoulder_y:
            current_time = time.time()
            if current_time - self.last_color_change_time > 1: 
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                rospy.set_param("/turtle/background_r", r)
                rospy.set_param("/turtle/background_g", g)
                rospy.set_param("/turtle/background_b", b)
                
                # 更新最近一次改变颜色的时间
                self.last_color_change_time = current_time
                
                self.response = self.clear.call()
            
        


        # 计算手臂向量
        vx = RElbow_x - RWrist_x
        vy = RElbow_y - RWrist_y
        
        # 计算手臂的长度
        v_length = math.sqrt(vx ** 2 + vy ** 2)

        # 计算与水平线的夹角
        if v_length == 0:
            return 0  # 避免除以零的情况
        
        # cos(theta) = vx / |v|
        cos_theta = vx / v_length
        
        # 使用反余弦函数计算角度（弧度）
        angle_rad = math.acos(cos_theta)
        
        # 将弧度转换为度数
        angle_deg = math.degrees(angle_rad)

        if RWrist_y > RElbow_y:
            angle_deg = -angle_deg

        # print('angle_deg:%f',angle_deg)


        # 0.392右——右上 分界线     1.178右上——上 分界线     1.963 上——左上 分界线      2.748 左上——左 分界线
        # 0.785 右上     1.570 上     2.355 左上      3.141 左
        if RWrist_y < 480 and RElbow_y < 480:
            if angle_deg>22.5 and angle_deg<67.5:
                # rospy.loginfo('上右')
                if self.twords>0.3927 and self.twords<1.1781:                
                    if self.twords<0.785:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    elif self.twords>0.785:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>-2.355 and self.twords<0.3927:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
            elif angle_deg > 112.5 and angle_deg < 157.5:
                # rospy.loginfo('上左')
                if self.twords>1.9635 and self.twords<2.7489:                
                    if self.twords<2.355:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    elif self.twords>2.355:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>-0.785 and self.twords<1.9635:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
                    
            elif angle_deg > 67.5 and angle_deg < 112.5:                
            # rospy.loginfo('上')
                if self.twords>1.178 and self.twords<1.9635:
                    if self.twords<1.57:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    elif self.twords>1.57:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>-1.57 and self.twords<1.1781:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
                    
            elif angle_deg < -22.5 and angle_deg > -67.5:
                # rospy.loginfo('下右')
                if self.twords<-0.3927 and self.twords>-1.1781:                
                    if self.twords>-0.78:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    elif self.twords<-0.78:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>2.355 or self.twords<-1.1781:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
                    
            elif angle_deg < -112.5 and angle_deg > -157.5:
                # rospy.loginfo('下左')
                if self.twords<-1.9635 and self.twords>-2.7489:                
                    if self.twords>-2.35:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    elif self.twords<-2.35:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>0.785 or self.twords<-2.7489:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
            elif angle_deg < -67.5 and angle_deg > -112.5:
                # rospy.loginfo('下')
                if self.twords<-1.1781 and self.twords>-1.9635:                
                    if self.twords<-1.57:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    elif self.twords>-1.57:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>1.57 or self.twords<-1.9635:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
                    
            elif angle_deg > -22.5 and angle_deg < 22.5:
                # rospy.loginfo('右')
                if self.twords<0.3927 and self.twords>-0.3927:                
                    if self.twords<0:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.2
                    elif self.twords>0:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=-0.2
                    else:
                        self.movemsg.linear.x=1
                        self.movemsg.angular.z=0.0
                else:
                    if self.twords>-3.14 and self.twords<-0.3927:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
                    
            elif angle_deg > 157.5 or angle_deg < -157.5:
                # print("左")
                if self.twords>=2.7489 and self.twords<3.13:
                    self.movemsg.linear.x=1
                    self.movemsg.angular.z=0.2

                elif self.twords<=-2.7489 and self.twords>-3.153:
                    self.movemsg.linear.x=1
                    self.movemsg.angular.z=-0.2

                elif self.twords>3.13 or self.twords<-3.153:
                    self.movemsg.linear.x=1
                    self.movemsg.angular.z=0

                else:
                    if self.twords>0:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=30
                    else:
                        self.movemsg.linear.x=0.1
                        self.movemsg.angular.z=-30
        else:
            self.movemsg.linear.x=0
            self.movemsg.angular.z=0
        self.turtle_move.publish(self.movemsg)


if __name__=='__main__':
    hand_turtle()

