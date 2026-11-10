#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import speech_recognition as sr
import pyttsx3
import cv2
import time
import os
import datetime



# =====================================
# TEXT TO SPEECH INITIALIZATION
# =====================================

engine = pyttsx3.init()

voices = engine.getProperty('voices')


for i, voice in enumerate(voices):
    print(f"{i}: {voice.name}")


if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)


# Polite and natural voice setting
engine.setProperty('rate',150)
engine.setProperty('volume',1.0)



def speak(text):

    print("Robot:", text)

    engine.say(text)

    engine.runAndWait()





# =====================================
# JUPITER ROBOT CAMERA USING ROS
# =====================================


class RobotCamera:


    def __init__(self):

        self.bridge = CvBridge()

        self.image_received = False

        self.image = None


        # Jupiter Robot Camera Topic

        img_topic = "/camera/color/image_raw"


        self.image_sub = rospy.Subscriber(
            img_topic,
            Image,
            self.callback
        )


        rospy.sleep(1)



    def callback(self,data):

        try:

            self.image = self.bridge.imgmsg_to_cv2(
                data,
                "bgr8"
            )


            self.image_received = True


        except CvBridgeError as e:

            print(e)



    def take_picture(self):


        if self.image_received:


            folder = "photos"


            if not os.path.exists(folder):

                os.makedirs(folder)



            filename = os.path.join(
                folder,
                "photo_" + time.strftime("%Y%m%d_%H%M%S") + ".jpg"
            )


            cv2.imwrite(
                filename,
                self.image
            )


            print("Photo saved:", filename)


            return True


        else:

            print("No camera image received")

            return False





# Global camera variable

robot_camera = None





# =====================================
# HOME ASSISTANT CHATBOT
# =====================================


def chatbot(question):


    question = question.lower().strip()



    # -------------------------------
    # Greeting
    # -------------------------------


    if "hello" in question or "hi" in question:

        return "yow G hows your day bro?"



    elif "morning" in question:

        return "morning bro."



    elif "good night" in question:

        return "Good night. Have a good rest."




    # -------------------------------
    # Robot Information
    # -------------------------------


    elif "what is your name" in question:

        return "My name is Rambo. I am your home assistant robot."



    elif "who made you" in question:

        return "I was created by Pancobis."



    elif "what can you do" in question:

        return "I can assist you at home, answer questions, and capture photos using my camera."



    # -------------------------------
    # Home Control
    # -------------------------------


    elif "turn on the light" in question:

        return "Okay. I will turn on the light."


    elif "turn off the light" in question:

        return "Okay. I will turn off the light."


    elif "turn on the fan" in question:

        return "Okay. I will turn on the fan."


    elif "turn off the fan" in question:

        return "Okay. I will turn off the fan."


    elif "open the door" in question:

        return "Okay. I will open the door."


    elif "close the door" in question:

        return "Okay. I will close the door."


    elif "lock the door" in question:

        return "The door has been locked for safety."


    elif "unlock the door" in question:

        return "The door has been unlocked."
        # -------------------------------
    # Home Monitoring
    # -------------------------------


    elif "check security" in question:

        return "Security system is checking your home."


    elif "is anyone home" in question:

        return "I will check the home status."


    elif "how is my house" in question:

        return "Your home condition is normal."





    # -------------------------------
    # Cleaning Assistant
    # -------------------------------


    elif "clean the house" in question:

        return "I will start the cleaning process."


    elif "start cleaning" in question:

        return "Cleaning process has started."


    elif "stop cleaning" in question:

        return "Cleaning process has stopped."





    # -------------------------------
    # Reminder
    # -------------------------------


    elif "remind me" in question:

        return "Sure. I will help you remember your task."





    # -------------------------------
    # Time and Date
    # -------------------------------


    elif "what time is it" in question:


        current_time = datetime.datetime.now().strftime("%I:%M %p")


        return "The current time is " + current_time




    elif "what is the date" in question:


        today = datetime.datetime.now().strftime("%d %B %Y")


        return "Today is " + today






    # -------------------------------
    # Weather
    # -------------------------------


    elif "what is the weather" in question:

        return "I need an internet connection to check live weather information."





    # -------------------------------
    # Jupiter Robot Camera
    # -------------------------------


    elif "take a picture" in question or "take photo" in question:


        success = robot_camera.take_picture()



        if success:

            return "The photo has been captured successfully."


        else:

            return "Sorry, I cannot capture the photo because the camera is not ready."






    # -------------------------------
    # Entertainment
    # -------------------------------


    elif "tell me a joke" in question:

        return "Why did the robot go to school? Because it wanted to improve its programming."


    elif "sing a song" in question:

        return "Sorry, I cannot sing yet, but I can assist you with other tasks."





    # -------------------------------
    # Goodbye
    # -------------------------------


    elif "bye" in question:

        return "Goodbye. Thank you for using my assistance."




    else:

        return "I am sorry, I do not understand your question. Please try again."







# =====================================
# GOOGLE SPEECH RECOGNITION
# =====================================


def googlesr():


    global robot_camera



    rospy.init_node(
        'home_assistant_robot',
        anonymous=True
    )



    # Start Jupiter camera

    robot_camera = RobotCamera()



    # Robot greeting when start

    speak(
        "Hello. Home assistant robot is ready. How can I help you?"
    )



    pub = rospy.Publisher(
        'result',
        String,
        queue_size=10
    )



    recognizer = sr.Recognizer()





    while not rospy.is_shutdown():



        with sr.Microphone() as source:



            print("\n======================")

            print("Home Assistant Ready")

            print("Listening...")



            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )



            try:


                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )



            except sr.WaitTimeoutError:


                print("No voice detected")

                continue






        try:



            question = recognizer.recognize_google(
                audio,
                language="en-US"
            )



            print("User:", question)



            answer = chatbot(question)



            print("Answer:", answer)



            speak(answer)



            pub.publish(answer)




            if "bye" in question.lower():


                rospy.signal_shutdown(
                    "Conversation ended"
                )





        except sr.UnknownValueError:



            print("Cannot understand speech")


            speak(
                "your voice is slow please repeat."
            )





        except sr.RequestError:



            print("Google speech error")


            speak(
                "Sorry, the speech recognition service is currently unavailable."
            )





        except Exception as e:


            print(e)


            speak(
                "Sorry, an unexpected error has occurred."
            )








# =====================================
# MAIN
# =====================================


if __name__ == '__main__':


    try:


        googlesr()



    except rospy.ROSInterruptException:


        pass