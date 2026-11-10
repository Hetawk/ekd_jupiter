#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
import cv2
import base64
import os
from openai import OpenAI
from datetime import datetime


class qwen_img_chat(object):

    def __init__(self):

        # 初始化 OpenAI 客户端（使用 DashScope）
        self.client = OpenAI(
            api_key=os.environ["EKD_DASHSCOPE_API_KEY"],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        # 图像保存路径
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        script_dir = os.path.dirname(os.path.realpath(__file__))  # 获取当前脚本所在的目录
        self.SAVE_PATH = f"{script_dir}/qwen_img_describe/describe_{timestamp}.png"

        rospy.init_node('image_to_qwen_node', anonymous=True)
        self.bridge = CvBridge()

        self.pub = rospy.Publisher("/qwen_img_out", String, queue_size=10)
        self.pub_q = rospy.Publisher("/qwen_img_out_question", String, queue_size=10)
        self.pub_tts = rospy.Publisher("/qwen_img_result", String, queue_size=10)
        self.pub_msg = String()
        # 订阅 /voiceWords 话题
        rospy.Subscriber("/qwen_img_in", String, self.voice_words_callback, queue_size=1)

        rospy.spin()

    # 编码图像为 Base64
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    # 调用 Qwen 进行图像分析
    def analyze_image_with_qwen(self, prompt, image_path):
        base64_image = self.encode_image(image_path)

        try:
            completion = self.client.chat.completions.create(
                model="qwen-omni-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                modalities=["text"],
                stream=True,
                stream_options={"include_usage": True}
            )
            content = ''
            print("Qwen 回复：")
            self.pub_msg = "\n=== 大模型回答 ===\n"
            rospy.sleep(1)
            self.pub.publish(self.pub_msg)
            for chunk in completion:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        print(delta.content, end='', flush=True)
                        self.pub_msg = delta.content
                        rospy.sleep(0.1)
                        self.pub.publish(self.pub_msg)

                        content += delta.content
                else:
                    # print("\nUsage:", chunk.usage)
                    pass
            print()
            self.pub_msg = content.replace('*', '')
            rospy.sleep(0.2)
            self.pub_tts.publish(self.pub_msg)
            

        except Exception as e:
            rospy.logerr("调用 Qwen 出错：%s", str(e))

    # 图像回调函数
    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
                # 调整图像大小以加快处理速度
                # cv_image = cv2.resize(cv_image, (1280, 720))

            # 保存图像
            rospy.loginfo("正在保存图像到 %s", self.SAVE_PATH)
            cv2.imwrite(self.SAVE_PATH, cv_image)



            # 分析图像
            self.analyze_image_with_qwen(self.prompt, self.SAVE_PATH)
            

        except CvBridgeError as e:
            rospy.logerr("CvBridge 错误: %s", e)
        except Exception as e:
            rospy.logerr("处理图像出错: %s", e)

    # /voiceWords 话题回调函数
    def voice_words_callback(self, msg):

        self.prompt = msg.data
        rospy.loginfo("接收到提示词: %s", self.prompt)

        self.pub_msg = '=== 问题 ===\n'+msg.data
        self.pub_q.publish(self.pub_msg)

        # 获取图像
        msg = rospy.wait_for_message("/camera/color/image_raw", Image)
        self.image_callback(msg)

    def image_show(self, msg):
        cv_image = CvBridge().imgmsg_to_cv2(msg, "bgr8")
        cv_image = cv2.resize(cv_image, (1024, 768))

        cv2.imshow("Image window", cv_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            rospy.signal_shutdown('Exit')
            cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        qwen_img_chat()
    except rospy.ROSInterruptException:
        pass