#!/usr/bin/env python
#
# RobotForAll www.robotforall.net
#
# Authors: Jeffrey Tan <i@jeffreytan.org>, Yong Cherng Liin (Leo)

import rospy
import rospkg
from std_msgs.msg import String, Bool
from subprocess import check_output

rospack = rospkg.RosPack()
pkg_path = rospack.get_path('rfa_gpt')

def get_cofig():
    input_topic = rospy.get_param('/rfa_gpt/INPUT_TOPIC')
    output_topic = rospy.get_param('/rfa_gpt/OUTPUT_TOPIC')
    return input_topic, output_topic

#initialize to get config
def init():
    rospy.init_node('rfa_gpt', anonymous=True)
    in_topic, out_topic = get_cofig()
    global pub 
    pub = rospy.Publisher(out_topic, String, queue_size=10)
    sub = rospy.Subscriber(in_topic, String, callback)

#How to call rfa_gpt with msg
def ask_gpt(msg):
    result = check_output(['python3.8',pkg_path+ '/scripts/gpt_call.py',msg, pkg_path])
    return result

def callback(data):
    msg = data.data
    if msg != '' or msg != None:
        response = ask_gpt(msg)
        response_str = response.decode("utf-8")
        print(response_str)
        pub.publish(response_str)

def main():
    init()
    rospy.spin() 
   
if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
    