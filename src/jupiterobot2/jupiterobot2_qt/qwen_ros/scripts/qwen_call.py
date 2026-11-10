#!/usr/bin/env python

import rospy
import os
from openai import OpenAI

from std_msgs.msg import String

class qwen_chat(object):
    def __init__(self):
        rospy.init_node('qwen_ros', anonymous=True)
        self.pub = rospy.Publisher("/qwen_out", String, queue_size=10)
        self.pub_q = rospy.Publisher("/qwen_out_question", String, queue_size=10)
        self.pub_tts = rospy.Publisher("/qwen_out_result", String, queue_size=10)
        self.qwen_msg = String()
        self.sub = rospy.Subscriber("/qwen_in", String, self.callback)
        rospy.spin()

    def qwen_llm(self, question):
        client = OpenAI(
            api_key=os.environ["EKD_DASHSCOPE_API_KEY"],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        completion = client.chat.completions.create(
            model="qwen3-32b",
            messages=[
                {"role": "system", "content": "你的名字是木星机器人,拥有人工智能相关的技能，如语音方面：语音合成、语音识别。图像方面：人脸检测、物体识别、人体姿态识别等。机械臂控制。建图与导航。人机交互等方面的技能。只回答语言不加动作。"},
                {"role": "user", "content": question},
            ],
            stream=True,
            stream_options={"include_usage": True},
            extra_body={"enable_thinking": True},  # 确保开启 Thinking 模式
        )

        # 用于保存完整的输出
        full_response = ""
        in_reasoning = True  # 是否还在输出 reasoning 阶段

        print('\n=== 问题 ===\n')

        print(question)
        self.qwen_msg.data = question
        self.pub_q.publish(self.qwen_msg)

        print('\n=== 思考 ===\n')
        self.qwen_msg.data = "\n=== 思考 ===\n"
        rospy.sleep(0.4)
        self.pub.publish(self.qwen_msg)
        for chunk in completion:
            if chunk.choices and hasattr(chunk.choices[0].delta, 'content'):
                choice = chunk.choices[0].delta
                # 判断是否有 reasoning_content（即是否处于思考阶段）
                if choice.reasoning_content is not None:
                    # 正在输出思考内容
                    print(f"{choice.reasoning_content}", end='', flush=True)
                    self.qwen_msg.data = choice.reasoning_content
                    self.pub.publish(self.qwen_msg)
                else:
                    # 开始正式输出 content，切换标志位
                    if in_reasoning:
                        print("\n=== 正式回答 ===\n")
                        self.qwen_msg.data = "\n=== 正式回答 ===\n"
                        self.pub.publish(self.qwen_msg)
                        in_reasoning = False
                    print(choice.content, end='', flush=True)
                    self.qwen_msg.data = choice.content
                    self.pub.publish(self.qwen_msg)
                    # 可选：拼接完整回答
                    full_response += choice.content
        return full_response


    def callback(self, data):
        msg = data.data
        if msg:
            response = self.qwen_llm(msg)
            print('\nresponse\n', response)
            cleaned_response = response.replace('*', '')
            self.pub_tts.publish(cleaned_response)


    

if __name__ == '__main__':
    try:
        qwen_chat()
    except rospy.ROSInterruptException:
        pass