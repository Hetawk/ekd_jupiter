#!/usr/bin/env python
#
# RobotForAll www.robotforall.net
#
# Authors: Jeffrey Tan <i@jeffreytan.org>

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge, CvBridgeError
import base64
import os
from openai import OpenAI

photo_taken = False

class ImageRecognition:

    def __init__(self):

        self.client = OpenAI(
            api_key = os.environ["EKD_QWEN_API_KEY"],
            base_url = "https://llm-orqx90gtcezlx878.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        )
        
        self.bridge = CvBridge()
        self.sub = rospy.Subscriber("/camera/color/image_raw", Image, self.image_callback)

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            global photo_taken
            if photo_taken == False:
                cv2.imwrite("photo.png", cv_image)
                photo_taken = True
                rospy.loginfo("The photo is taken.")
                # Get response from VLM
                self.get_response()
        except CvBridgeError as e:
            print(e)

    def get_response(self):
        prompt = "Give me a description?"
        with open("photo.png", "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        completion = self.client.chat.completions.create(
            model="qwen3.8-max",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"},}
                    ],
                }
            ],
        )

        rospy.loginfo(completion.choices[0].message.content)
        cv_photo = cv2.imread("photo.png")
        cv2.imshow('Photo',cv_photo)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == '__main__':

    # Initialize
    rospy.init_node('image_recognition', anonymous=False)
    ImageRecognition()
    rospy.spin()
