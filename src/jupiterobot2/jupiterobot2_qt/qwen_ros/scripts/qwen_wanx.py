#!/usr/bin/env python

from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os
import rospy
from std_msgs.msg import String


# prompt = "一只在沙滩上的小白兔"
api_key = os.environ["EKD_DASHSCOPE_API_KEY"]

def wanx_generation(msg):
    prompt = msg.data
    print('----sync call, please wait a moment----')
    rsp = ImageSynthesis.call(api_key=api_key,
                            model="wanx2.1-t2i-turbo",
                            prompt=prompt,
                            n=1,
                            size='1086*700')
    print('response: %s' % rsp)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(script_dir, "qwen_pictures")

    if not os.path.exists(directory):
        os.makedirs(directory)
    if rsp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图片
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]

            actual_prompt = result.actual_prompt
            actual_prompt_msg.data = actual_prompt
            print("\nactual_prompt", actual_prompt)


            file_path = os.path.join(directory, file_name)
            print(file_path)
            pub_msg.data = file_path
            with open(file_path, 'wb+') as f:
                f.write(requests.get(result.url).content)
            pub_result.publish(pub_msg)
            pub_actual_prompt.publish(actual_prompt_msg)
    else:
        print('sync_call Failed, status_code: %s, code: %s, message: %s' %
            (rsp.status_code, rsp.code, rsp.message))
        pub_msg.data = "Failed"
        pub_result.publish(pub_msg)
    

if __name__=="__main__":
    rospy.init_node("qwen_wanx")
    rospy.Subscriber("wanx_prompt", String, wanx_generation, queue_size=1)
    pub_result = rospy.Publisher("wanx_result", String, queue_size=1)
    pub_msg = String()
    pub_actual_prompt = rospy.Publisher("wanx_actual_prompt", String, queue_size=1)
    actual_prompt_msg = String()
    

    rospy.spin()