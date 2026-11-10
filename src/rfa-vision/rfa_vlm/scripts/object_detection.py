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
import json

photo_taken = False

class ObjectDetection:

    def __init__(self):

        api_key = os.environ.get("EKD_QWEN_API_KEY")
        if not api_key:
            raise RuntimeError("EKD_QWEN_API_KEY is unset; source ~/ekd_catkin_ws/setup_ekd.bash")
        self.client = OpenAI(
            api_key = api_key,
            # Original OpenAI endpoint: base_url = "https://api.openai.com/v1"
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
        prompt = "Use bounding boxes to locate each object in the image. Output the coordinates of all bounding boxes with the object labels in JSON format, use label as the name of label and bbox_2d as the name of the bounding box for the objects JSON. Show only the final JSON output without the ```json```."
        with open("photo.png", "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        completion = self.client.chat.completions.create(
            # Previous model: "gpt-4o-mini"
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

        self.result = completion.choices[0].message.content
        rospy.loginfo(self.result)
        self.update_photo()

    def update_photo(self):
        data = json.loads(self.result)
        objects = data["objects"]
        image = cv2.imread("photo.png")

        for obj in objects:
            bbox = obj['bbox_2d']
            label = obj['label']
            
            x_min, y_min, x_max, y_max = bbox
            color = (255, 0, 0)
            
            # Draw rectangle
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)
            
            # Put label text above the bounding box
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, label, (x_min, y_min - 10), font, 0.5, color, 2)

        # Save and display output
        cv2.imwrite('output_photo.png', image)
        cv2.imshow('Annotated Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == '__main__':

    # Initialize
    rospy.init_node('take_photo', anonymous=False)
    ObjectDetection()
    rospy.spin()
