#Simple function that take user input and print out response
#
# RobotForAll www.robotforall.net
#
# Authors: Jeffrey Tan <i@jeffreytan.org>, Yong Cherng Liin (Leo)

import yaml
import sys
import os
from datetime import datetime
from openai import OpenAI

#get data from config file
def get_cofig(config_file):
    v = {}
    with open(config_file,'r') as file:
        v = yaml.load(file, Loader=yaml.SafeLoader)
        global client, set_model
        # Select credentials from the EKD_* environment; setup_ekd.bash loads .env. Never hard-code keys.
        key_environment = {
            'var.yaml': 'EKD_OPENAI_API_KEY',
            'deepseek.yaml': 'EKD_DEEPSEEK_API_KEY',
            'qwen.yaml': 'EKD_QWEN_API_KEY',
        }.get(os.path.basename(config_file))
        api_key = os.environ.get(key_environment) if key_environment else None
        if not api_key:
            raise RuntimeError(
                f'{key_environment or "API key variable"} is unset; '
                'source ~/ekd_catkin_ws/setup_ekd.bash')
        client = OpenAI(
            api_key = api_key,
            base_url= v['BASE_URL'],
        )
        set_model = v['MODEL']
    return v

#initialize to get config
def init(pkg_path):
    config_file = pkg_path+'/config/deepseek.yaml'
    var_list = get_cofig(config_file)
    return var_list

#get response and calculate number of token in prompting
def get_completion_and_token_count(
                                    messages,
                                    temperature=0,
                                    max_tokens=500):

    response = client.chat.completions.create(
        model=set_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content

    token_dict = {
        'prompt_tokens':response.usage.prompt_tokens,
        'completion_tokens':response.usage.completion_tokens,
        'total_tokens':response.usage.total_tokens,
    }

    return content, token_dict

##the prompting function after receive user input
def get_response( var_list,input):
    #get the current time
    now = datetime.now()
    current_time = now.strftime('%I:%M %p')
    current_pose = "Auditorium"
    delimiter = "####"
    system_message = f"""
    {var_list['TITLE']}
    The current time is {current_time}
    the robot's location is {current_pose} \
    {var_list['PROMPT']}
    The input will be delimited with \
    {delimiter} characters.
    {var_list['INFO']}
    
    """
    user_message = f"""\
    {input}"""
    messages =  [
    {'role':'system',
    'content': system_message},
    {'role':'user',
    'content': f"{delimiter}{user_message}{delimiter}"},
    ]

    response, token_count = get_completion_and_token_count(messages)

    return response, token_count

def main():
    msg = sys.argv[1]
    pkg_path = sys.argv[2]
    var_list = init(pkg_path)
    
    response, token_count = get_response(var_list, msg)
    print(response)
    return response

if __name__ == "__main__":
    main()
