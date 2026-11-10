#!/usr/bin/env python3
import os
import rospy
import pygame
import random
import threading
import cv2
import numpy as np
import mediapipe as mp
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Bool
import time
import math

def play_wav(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

class PoseGameSystem:
    def __init__(self):
        rospy.init_node('pose_game_system')
        
        # ROS 初始化
        self.bridge = CvBridge()
        self.jump_event = threading.Event()
        self.latest_image = None
        self.display_image = None
        self.pose_status = "No arms detected"
        self.swing_status = ""
        self.jump_triggered = False
        self.last_jump_time = 0
        self.script_dir = os.path.dirname(os.path.realpath(__file__))  # 获取当前脚本所在的目录
        self.parent_dir = os.path.dirname(self.script_dir)  # 获取父目录
        self.media_path = os.path.join(self.parent_dir, "media")

        
        # 姿势识别参数 - 初始化 MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        
        # 手臂检测参数
        self.jump_line_length = 0.6  # 跳跃线的长度（相对于图像高度）
        
        # 用于存储上一帧的手臂位置
        self.prev_left_wrist = None
        self.prev_right_wrist = None
        self.prev_left_elbow = None
        self.prev_right_elbow = None
        self.last_swing_time = 0
        
        # 穿越检测状态
        self.left_arm_crossing = False
        self.right_arm_crossing = False
        self.left_arm_last_side = None
        self.right_arm_last_side = None
        self.change_color_duration = 0.5
        
        # 游戏参数
        self.game_params = {
            'WIDTH': 800,
            'HEIGHT': 600,
            'FPS': 60,
            'GRAVITY': 0.2,
            'JUMP_FORCE': -6.5,
            'PLAYER_SIZE': 40,
            'OBSTACLE_WIDTH': 80,
            'OBSTACLE_GAP': 250,
            'OBSTACLE_SPEED': 5,
            'BG_COLOR': (25, 25, 40),
            'PLAYER_COLOR': (50, 180, 255),
            'OBSTACLE_COLOR': (220, 100, 100),
            'TEXT_COLOR': (220, 220, 220),
            'SCORE_COLOR': (255, 215, 0),
            'ACTION_COLOR': (255, 200, 0),
            'TEXT_COLOR2': (255, 140, 0),
            'TEXT_COLOR3': (237, 85, 106),
            'JUMP_LINE_COLOR': (0, 255, 255),  # 跳跃线颜色
            'ARM_LINE_COLOR': (255, 0, 255),   # 手臂线颜色
            'LIVES': 3,                         # 初始生命值
            'INVULNERABLE_TIME': 4000,          # 无敌时间（毫秒）
            'HEART_SIZE': 30,                   # 爱心大小
            'HEART_SPACING': 40,               # 爱心间距
            'HEART_COLOR': (255, 50, 50)       # 爱心颜色
        }
        
        # 加载玩家图像
        self.player_image = self.load_player_image()
        
        # 加载背景图像
        self.background_image = self.load_background_image()
        
        # 加载障碍物图像
        self.obstacle_images = self.load_obstacle_images()
        
        # 加载爱心图像
        self.heart_image = self.load_heart_image()

        #加载灰色爱心图像
        self.heart_gray_image = self.load_gray_heart_image()

        # 游戏状态
        self.game_state = {
            'player_y': self.game_params['HEIGHT'] // 2,
            'player_vel': 0,
            'obstacles': [],
            'score': 0,
            'lives': self.game_params['LIVES'],  # 当前生命值
            'game_over': False,
            'game_started': False,
            'obstacle_timer': 0,
            'obstacle_frequency': 1800,  # 毫秒
            'invulnerable': False,        # 是否处于无敌状态
            'invulnerable_start_time': 0,  # 无敌状态开始时间
            'player_reset_pos': self.game_params['HEIGHT'] // 2,  # 玩家复活位置
            'can_jump_from_bottom': False  # 新增：是否可以从底部跳跃
        }
        
        # 图像订阅
        self.image_sub = rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)
        
        # 启动线程
        self.pose_thread = threading.Thread(target=self.pose_processing)
        self.game_thread = threading.Thread(target=self.run_game)
        self.camera_window_thread = threading.Thread(target=self.show_camera_window)
        
        self.pose_thread.daemon = True
        self.game_thread.daemon = True
        self.camera_window_thread.daemon = True
        
        rospy.loginfo("Pose Game System Started")
        rospy.loginfo("Using arm alignment detection with crossing detection")

    def load_player_image(self):
        """加载玩家图像，如果找不到则创建默认图像"""
        try:
            # 尝试加载图像文件
            image_path = os.path.join(os.path.dirname(__file__), f"{self.media_path}/bird.png")
            player_image = pygame.image.load(image_path)
            # 调整图像大小
            player_image = pygame.transform.scale(player_image, 
                                                (self.game_params['PLAYER_SIZE'], 
                                                 self.game_params['PLAYER_SIZE']))
            return player_image
        except:
            # 如果找不到图像，创建默认的玩家图像
            rospy.logwarn("Player image not found, creating default player")
            surf = pygame.Surface((self.game_params['PLAYER_SIZE'], self.game_params['PLAYER_SIZE']), pygame.SRCALPHA)
            pygame.draw.circle(surf, (50, 180, 255), (self.game_params['PLAYER_SIZE']//2, self.game_params['PLAYER_SIZE']//2), self.game_params['PLAYER_SIZE']//3)
            pygame.draw.circle(surf, (255, 255, 255), (self.game_params['PLAYER_SIZE']//3, self.game_params['PLAYER_SIZE']//3), 5)
            pygame.draw.circle(surf, (255, 255, 255), (2*self.game_params['PLAYER_SIZE']//3, self.game_params['PLAYER_SIZE']//3), 5)
            pygame.draw.arc(surf, (255, 100, 100), 
                           [self.game_params['PLAYER_SIZE']//4, self.game_params['PLAYER_SIZE']//2, 
                            self.game_params['PLAYER_SIZE']//2, self.game_params['PLAYER_SIZE']//3], 
                           0, 3.14, 3)
            return surf
    
    def load_background_image(self):
        """加载背景图像，如果找不到则创建默认背景"""
        try:
            # 尝试加载背景图像
            bg_path = os.path.join(os.path.dirname(__file__),f"{self.media_path}/sky.png")
            bg_image = pygame.image.load(bg_path)
            # 调整图像大小以匹配游戏窗口
            bg_image = pygame.transform.scale(bg_image, 
                                             (self.game_params['WIDTH'], 
                                              self.game_params['HEIGHT']))
            return bg_image
        except Exception as e:
            # 如果找不到图像，创建默认的背景
            rospy.logwarn(f"Background image not found: {e}, creating default background")
            surf = pygame.Surface((self.game_params['WIDTH'], self.game_params['HEIGHT']))
            # 创建渐变背景
            for y in range(self.game_params['HEIGHT']):
                # 从深蓝色渐变到浅蓝色
                color = (25, 25, 40 + int(100 * y / self.game_params['HEIGHT']))
                pygame.draw.line(surf, color, (0, y), (self.game_params['WIDTH'], y))
            
            # 添加一些星星
            for _ in range(100):
                x = random.randint(0, self.game_params['WIDTH'])
                y = random.randint(0, self.game_params['HEIGHT'])
                size = random.randint(1, 3)
                brightness = random.randint(150, 255)
                pygame.draw.circle(surf, (brightness, brightness, brightness), (x, y), size)
            
            return surf
    
    def load_obstacle_images(self):
        """加载障碍物图像，如果找不到则创建默认图像"""
        obstacle_images = {
            'top': None,
            'bottom': None
        }
        
        try:
            # 加载障碍物图像文件
            obstacle_path = os.path.join(os.path.dirname(__file__), f"{self.media_path}/obstacle.png")
            obstacle_img = pygame.image.load(obstacle_path)
            
            # 调整图像大小
            obstacle_width = self.game_params['OBSTACLE_WIDTH']
            obstacle_height = self.game_params['HEIGHT']

            # 创建上方障碍物图像（倒置）
            top_img = pygame.transform.scale(obstacle_img, (obstacle_width, obstacle_height))
            top_img = pygame.transform.flip(top_img, False, True)  # 垂直翻转
            
            # 创建下方障碍物图像
            bottom_img = pygame.transform.scale(obstacle_img, (obstacle_width, obstacle_height))
            
            obstacle_images['top'] = top_img
            obstacle_images['bottom'] = bottom_img
            
            rospy.loginfo("Obstacle images loaded successfully")
        except Exception as e:
            # 如果找不到图像，创建默认的障碍物图像
            rospy.logwarn(f"Obstacle image not found: {e}, creating default obstacles")
            
            # 创建上方障碍物图像
            top_img = pygame.Surface((self.game_params['OBSTACLE_WIDTH'], self.game_params['HEIGHT']), pygame.SRCALPHA)
            pygame.draw.rect(top_img, (220, 100, 100), (0, 0, self.game_params['OBSTACLE_WIDTH'], self.game_params['HEIGHT']))
            pygame.draw.rect(top_img, (180, 70, 70), (0, self.game_params['HEIGHT'] - 20, self.game_params['OBSTACLE_WIDTH'], 20))
            
            # 创建下方障碍物图像
            bottom_img = pygame.Surface((self.game_params['OBSTACLE_WIDTH'], self.game_params['HEIGHT']), pygame.SRCALPHA)
            pygame.draw.rect(bottom_img, (220, 100, 100), (0, 0, self.game_params['OBSTACLE_WIDTH'], self.game_params['HEIGHT']))
            pygame.draw.rect(bottom_img, (180, 70, 70), (0, 0, self.game_params['OBSTACLE_WIDTH'], 20))
            
            obstacle_images['top'] = top_img
            obstacle_images['bottom'] = bottom_img
        
        return obstacle_images
    
    def load_heart_image(self):
        """加载爱心图像，如果找不到则创建默认爱心"""
        try:
            # 尝试加载爱心图像文件
            heart_path = os.path.join(os.path.dirname(__file__), f"{self.media_path}/heart.png")
            heart_image = pygame.image.load(heart_path)
            # 调整图像大小
            heart_image = pygame.transform.scale(heart_image, 
                                                (self.game_params['HEART_SIZE'], 
                                                 self.game_params['HEART_SIZE']))
            return heart_image
        except:
            # 如果找不到图像，创建默认的爱心
            rospy.logwarn("Heart image not found, creating default heart")
            surf = pygame.Surface((self.game_params['HEART_SIZE'], self.game_params['HEART_SIZE']), pygame.SRCALPHA)
            # 绘制一个简单的爱心形状
            center_x = self.game_params['HEART_SIZE'] // 2
            center_y = self.game_params['HEART_SIZE'] // 2
            radius = self.game_params['HEART_SIZE'] // 4
            
            # 左半圆
            pygame.draw.circle(surf, self.game_params['HEART_COLOR'], 
                              (center_x - radius // 2, center_y - radius // 2), radius)
            # 右半圆
            pygame.draw.circle(surf, self.game_params['HEART_COLOR'], 
                              (center_x + radius // 2, center_y - radius // 2), radius)
            
            # 三角形部分
            points = [
                (center_x - radius - 2, center_y - radius // 2 + 2),
                (center_x + radius + 2, center_y - radius // 2 + 2),
                (center_x, center_y + radius)
            ]
            pygame.draw.polygon(surf, self.game_params['HEART_COLOR'], points)
            return surf

    def load_gray_heart_image(self):
        """创建灰色爱心图像"""
        try:
            # 尝试加载爱心图像文件
            heart_path = os.path.join(os.path.dirname(__file__), f"{self.media_path}/heart_gray.png")
            heart_gray_image = pygame.image.load(heart_path)
            # 调整图像大小
            heart_gray_image = pygame.transform.scale(heart_gray_image, 
                                                (self.game_params['HEART_SIZE'], 
                                                self.game_params['HEART_SIZE']))
            return heart_gray_image
        except:
            # 如果找不到图像，创建默认的灰色爱心
            rospy.logwarn("Heart image not found, creating default gray heart")
            surf = pygame.Surface((self.game_params['HEART_SIZE'], self.game_params['HEART_SIZE']), pygame.SRCALPHA)
            # 绘制一个简单的爱心形状
            center_x = self.game_params['HEART_SIZE'] // 2
            center_y = self.game_params['HEART_SIZE'] // 2
            radius = self.game_params['HEART_SIZE'] // 4
            
            # 左半圆
            pygame.draw.circle(surf, self.game_params['GRAY_HEART_COLOR'], 
                            (center_x - radius // 2, center_y - radius // 2), radius)
            # 右半圆
            pygame.draw.circle(surf, self.game_params['GRAY_HEART_COLOR'], 
                            (center_x + radius // 2, center_y - radius // 2), radius)
            
            # 三角形部分
            points = [
                (center_x - radius - 2, center_y - radius // 2 + 2),
                (center_x + radius + 2, center_y - radius // 2 + 2),
                (center_x, center_y + radius)
            ]
            pygame.draw.polygon(surf, self.game_params['GRAY_HEART_COLOR'], points)
            return surf

    def image_callback(self, msg):
        try:
            self.latest_image = cv2.flip(self.bridge.imgmsg_to_cv2(msg, "bgr8"), 1)
        except Exception as e:
            rospy.logerr(f"Image conversion error: {e}")

    def pose_processing(self):
        while not rospy.is_shutdown():
            if self.latest_image is not None:
                try:
                    # 创建一个副本用于处理
                    processing_image = self.latest_image.copy()
                    height, width, _ = processing_image.shape
                    
                    # 处理姿势识别
                    image_rgb = cv2.cvtColor(processing_image, cv2.COLOR_BGR2RGB)
                    results = self.pose.process(image_rgb)
                    
                    # 重置状态
                    self.pose_status = "No arms detected"
                    self.swing_status = ""
                    self.jump_triggered = False
                    
                    if results.pose_landmarks:
                        # 绘制姿势关键点
                        mp.solutions.drawing_utils.draw_landmarks(
                            processing_image, 
                            results.pose_landmarks,
                            self.mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style())
                        
                        # 获取手臂关键点 (肘部和手腕)
                        landmarks = results.pose_landmarks.landmark
                        
                        # 左臂关键点
                        left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW]
                        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
                        
                        # 右臂关键点
                        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
                        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]

                        # 获取图像尺寸
                        h, w, _ = processing_image.shape

                        # 将归一化坐标转换为像素坐标
                        left_wrist_px = (int(left_wrist.x * w), int(left_wrist.y * h))
                        right_wrist_px = (int(right_wrist.x * w), int(right_wrist.y * h))

                        # 画一个红色的实心圆（手腕位置）
                        radius = 10  # 圆的半径
                        color = (0, 255, 0)  # 红色 (BGR 格式)
                        thickness = -1  # -1 表示实心圆

                        cv2.circle(processing_image, left_wrist_px, radius, color, thickness)
                        cv2.circle(processing_image, right_wrist_px, radius, color, thickness)
                        
                        # 检查当前帧是否有有效点
                        left_arm_visible = left_elbow.visibility > 0.5 and left_wrist.visibility > 0.5
                        right_arm_visible = right_elbow.visibility > 0.5 and right_wrist.visibility > 0.5
                        
                        if left_arm_visible or right_arm_visible:
                            self.pose_status = "Arms detected"
                            
                            current_time = time.time()
                            
                            # 分别检查左臂和右臂的挥动
                            swing_detected = False
                            
                            # 绘制跳跃线并检测对齐
                            if left_arm_visible:
                                # 计算手肘位置（像素坐标）
                                elbow_x = int(left_elbow.x * width)
                                elbow_y = int(left_elbow.y * height)
                                
                                # 计算手腕位置（像素坐标）
                                wrist_x = int(left_wrist.x * width)
                                wrist_y = int(left_wrist.y * height)
                                
                                # 计算跳跃线终点（竖直向上）
                                jump_line_end_y = int(max(0, elbow_y - self.jump_line_length * height))
                                
                                # 绘制跳跃线（从肘部向上）
                                cv2.line(processing_image, (elbow_x, elbow_y), 
                                        (elbow_x, 0), 
                                        self.game_params['JUMP_LINE_COLOR'], 3)
                                
                                # 绘制手臂线（从肘部到手腕）
                                cv2.line(processing_image, (elbow_x, elbow_y), 
                                        (wrist_x, wrist_y), 
                                        self.game_params['ARM_LINE_COLOR'], 2)
                                    
                                # 检测穿越事件（从左到右或从右到左）
                                current_side = "right" if wrist_x > elbow_x else "left"
                                
                                # 如果之前没有记录位置，初始化
                                if self.left_arm_last_side is None:
                                    self.left_arm_last_side = current_side
                                
                                # 检查穿越事件
                                if self.left_arm_last_side != current_side:
                                    # 检测到穿越
                                    if not self.left_arm_crossing:
                                        swing_detected = True
                                        self.swing_status = f"Left arm crossed ({self.left_arm_last_side}->{current_side})"
                                        self.left_arm_crossing = True

                                        radius = 20
                                        current_time1 = time.time()
                                        self.color_change_start_time = current_time1
        
                                        # 判断是否在颜色改变期间
                                        if current_time1 - self.color_change_start_time < self.change_color_duration:
                                            color = (0, 255, 255)  # 黄色
                                        else:
                                            color = (0, 0, 255)  # 红色
                                        
                                        # 绘制实心圆
                                        cv2.circle(processing_image, left_wrist_px, radius, color, -1)
                                        
                                        # 如果超过了指定时间，重置穿越标志
                                        if current_time1 - self.color_change_start_time >= self.change_color_duration:
                                            self.right_arm_crossing = False
                                else:
                                    self.left_arm_crossing = False
                                
                                # 更新最后位置
                                self.left_arm_last_side = current_side
                            
                            if right_arm_visible:
                                # 计算手肘位置（像素坐标）
                                elbow_x = int(right_elbow.x * width)
                                elbow_y = int(right_elbow.y * height)
                                
                                # 计算手腕位置（像素坐标）
                                wrist_x = int(right_wrist.x * width)
                                wrist_y = int(right_wrist.y * height)
                                
                                # 计算跳跃线终点（竖直向上）
                                jump_line_end_y = int(max(0, elbow_y - self.jump_line_length * height))
                                
                                # 绘制跳跃线（从肘部向上）
                                cv2.line(processing_image, (elbow_x, elbow_y), 
                                        (elbow_x, jump_line_end_y), 
                                        self.game_params['JUMP_LINE_COLOR'], 3)
                                
                                # 绘制手臂线（从肘部到手腕）
                                cv2.line(processing_image, (elbow_x, elbow_y), 
                                        (wrist_x, wrist_y), 
                                        self.game_params['ARM_LINE_COLOR'], 2)
                                
                                # 检测穿越事件（从左到右或从右到左）
                                current_side = "right" if wrist_x > elbow_x else "left"
                                
                                # 如果之前没有记录位置，初始化
                                if self.right_arm_last_side is None:
                                    self.right_arm_last_side = current_side
                                
                                # 检查穿越事件
                                if self.right_arm_last_side != current_side:
                                    # 检测到穿越
                                    if not self.right_arm_crossing:
                                        swing_detected = True
                                        self.swing_status = f"Right arm crossed ({self.right_arm_last_side}->{current_side})"
                                        self.right_arm_crossing = True

                                        
                                        radius = 20
                                        current_time1 = time.time()
                                        self.color_change_start_time = current_time1
        
                                        # 判断是否在颜色改变期间
                                        if current_time1 - self.color_change_start_time < self.change_color_duration:
                                            color = (0, 255, 255)  # 黄色
                                        else:
                                            color = (0, 0, 255)  # 红色
                                        
                                        # 绘制实心圆
                                        cv2.circle(processing_image, right_wrist_px, radius, color, -1)
                                        
                                        # 如果超过了指定时间，重置穿越标志
                                        if current_time1 - self.color_change_start_time >= self.change_color_duration:
                                            self.right_arm_crossing = False

                                else:
                                    self.right_arm_crossing = False
                                
                                # 更新最后位置
                                self.right_arm_last_side = current_side
                            
                            # 如果检测到对齐动作
                            if swing_detected:
                                # 触发跳跃
                                self.jump_event.set()
                                self.jump_triggered = True
                                self.last_swing_time = current_time
                                self.last_jump_time = current_time
                            
                            # 更新上一帧的关键点位置
                            if left_arm_visible:
                                self.prev_left_wrist = left_wrist
                                self.prev_left_elbow = left_elbow
                            else:
                                self.prev_left_wrist = None
                                self.prev_left_elbow = None
                                self.left_arm_last_side = None
                                self.left_arm_crossing = False
                            
                            if right_arm_visible:
                                self.prev_right_wrist = right_wrist
                                self.prev_right_elbow = right_elbow
                            else:
                                self.prev_right_wrist = None
                                self.prev_right_elbow = None
                                self.right_arm_last_side = None
                                self.right_arm_crossing = False
                        else:
                            # 关键点不可见，重置上一帧数据
                            self.prev_left_wrist = None
                            self.prev_left_elbow = None
                            self.prev_right_wrist = None
                            self.prev_right_elbow = None
                            self.left_arm_last_side = None
                            self.right_arm_last_side = None
                            self.left_arm_crossing = False
                            self.right_arm_crossing = False
                    
                    # 在图像上添加姿势状态和挥动状态
                    cv2.putText(processing_image, self.pose_status, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)
                    
                    
                    # 添加跳跃触发状态
                    if self.jump_triggered:
                        action_text = "JUMP TRIGGERED!" if not self.game_state['game_over'] else "RESTART GAME!"
                        cv2.putText(processing_image, action_text, (10, 160), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
                    
                    # 添加游戏状态
                    game_status = "Game: "
                    if not self.game_state['game_started']:
                        game_status += "READY"
                    elif self.game_state['game_over']:
                        game_status += "GAME OVER"
                    else:
                        game_status += "PLAYING"
                    cv2.putText(processing_image, game_status, (processing_image.shape[1] - 200, 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    # 添加操作提示
                    if self.game_state['game_over']:
                        cv2.putText(processing_image, "Cross jump line to restart game", 
                                   (10, processing_image.shape[0] - 80), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
                    elif not self.game_state['game_started']:
                        cv2.putText(processing_image, "Cross jump line to start game", 
                                   (10, processing_image.shape[0] - 80), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
                    else:
                        cv2.putText(processing_image, "Cross jump line to jump", 
                                   (10, processing_image.shape[0] - 80), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
                    
                    # 更新显示图像
                    self.display_image = processing_image
                
                except Exception as e:
                    rospy.logerr(f"Pose processing error: {e}")
                    import traceback
                    rospy.logerr(traceback.format_exc())
                    self.display_image = self.latest_image.copy() if self.latest_image is not None else None
            
            # 控制处理频率
            rospy.sleep(0.05)

    def show_camera_window(self):
        """显示摄像头窗口，实时展示姿势识别结果"""
        cv2.namedWindow("Pose Recognition Monitor", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Pose Recognition Monitor", 640, 480)
        
        while not rospy.is_shutdown():
            if self.display_image is not None:
                try:
                    # 显示图像
                    cv2.imshow("Pose Recognition Monitor", self.display_image)
                    
                    # 更新窗口
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        rospy.signal_shutdown("User pressed Q")
                        break
                except Exception as e:
                    rospy.logerr(f"Camera window error: {e}")
            else:
                # 创建黑色背景
                blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank_image, "Waiting for camera feed...", 
                            (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.imshow("Pose Recognition Monitor", blank_image)
                cv2.waitKey(1)
                
            rospy.sleep(0.02)
        
        cv2.destroyAllWindows()

    def get_fps(self):
        """计算姿势识别的帧率"""
        if not hasattr(self, 'last_time'):
            self.last_time = rospy.Time.now()
            self.frame_count = 0
            return 0
        
        self.frame_count += 1
        current_time = rospy.Time.now()
        elapsed = (current_time - self.last_time).to_sec()
        
        if elapsed > 1.0:  # 每秒钟计算一次FPS
            fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_time = current_time
            return fps
        
        return -1  # 表示还没有足够的帧计算FPS

    def spawn_obstacle(self):
        if self.game_state['score'] >= 15:
            self.game_params['OBSTACLE_GAP'] = 225
        if self.game_state['score'] >= 30:
            self.game_params['OBSTACLE_GAP'] = 200
        if self.game_state['score'] >= 50:
            self.game_params['OBSTACLE_GAP'] = 175

        gap_y = random.randint(150, self.game_params['HEIGHT'] - 150)
        obstacle = {
            'x': self.game_params['WIDTH'],
            'top_height': gap_y - self.game_params['OBSTACLE_GAP'] // 2,
            'bottom_y': gap_y + self.game_params['OBSTACLE_GAP'] // 2,
            'passed': False
        }
        self.game_state['obstacles'].append(obstacle)

    def reset_game(self):
        self.game_state = {
            'player_y': self.game_params['HEIGHT'] // 2,
            'player_vel': 0,
            'obstacles': [],
            'score': 0,
            'lives': self.game_params['LIVES'],
            'game_over': False,
            'game_started': True,
            'obstacle_timer': 0,
            'obstacle_frequency': 1800,
            'invulnerable': False,
            'invulnerable_start_time': 0,
            'player_reset_pos': self.game_params['HEIGHT'] // 2,
            'can_jump_from_bottom': False  # 重置标志
        }
        # 游戏开始时立即生成第一个障碍物
        self.spawn_obstacle()
        
    def respawn_player(self):
        """复活玩家，保留当前分数和生命值"""
        self.game_state['player_y'] = self.game_state['player_reset_pos']
        self.game_state['player_vel'] = 0
        self.game_state['obstacles'] = []  # 清空障碍物
        self.game_state['obstacle_timer'] = 0
        self.game_state['invulnerable'] = True
        self.game_state['invulnerable_start_time'] = pygame.time.get_ticks()
        self.game_state['can_jump_from_bottom'] = True  # 允许从底部跳跃
        # 生成一个新的障碍物
        self.spawn_obstacle()

    def run_game(self):
        # 初始化pygame
        pygame.init()
        screen = pygame.display.set_mode(
            (self.game_params['WIDTH'], self.game_params['HEIGHT']))
        pygame.display.set_caption("ROS Pose Jump Game")
        clock = pygame.time.Clock()
        
        last_time = pygame.time.get_ticks()
        
        running = True
        while running and not rospy.is_shutdown():
            current_time = pygame.time.get_ticks()
            delta_time = current_time - last_time
            last_time = current_time
            
            # 处理事件
            key_jumped = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        key_jumped = True
                        if self.game_state['game_over']:
                            self.reset_game()
                        elif not self.game_state['game_started']:
                            self.reset_game()
                        else:
                            self.game_state['player_vel'] = self.game_params['JUMP_FORCE']
                    elif event.key == pygame.K_q:
                        rospy.signal_shutdown("User pressed Q")
                        running = False
            
            # 处理姿势跳跃/重新开始
            jumped_by_pose = False
            if self.jump_event.is_set():
                jumped_by_pose = True
                # 游戏结束状态：重新开始游戏
                if self.game_state['game_over']:
                    self.reset_game()
                    self.jump_triggered = True
                
                # 游戏未开始状态：开始游戏
                elif not self.game_state['game_started']:
                    self.reset_game()
                
                # 游戏进行中：执行跳跃
                elif self.game_state['game_started'] and not self.game_state['game_over']:
                    # 允许从底部跳跃
                    if self.game_state['can_jump_from_bottom'] or self.game_state['player_y'] < self.game_params['HEIGHT'] - self.game_params['PLAYER_SIZE']:
                        self.game_state['player_vel'] = self.game_params['JUMP_FORCE']
                        play_wav(f"{self.media_path}/birdwave.MP3")
                
                self.jump_event.clear()
            
            # 更新无敌状态
            if self.game_state['invulnerable']:
                elapsed_time = current_time - self.game_state['invulnerable_start_time']
                if elapsed_time > self.game_params['INVULNERABLE_TIME']:
                    self.game_state['invulnerable'] = False
                    self.game_state['can_jump_from_bottom'] = False  # 无敌时间结束后禁止从底部跳跃
            
            # 更新游戏状态
            if self.game_state['game_started'] and not self.game_state['game_over']:
                # 更新玩家位置
                self.game_state['player_vel'] += self.game_params['GRAVITY']
                self.game_state['player_y'] += self.game_state['player_vel']
                
                # 边界检查
                if self.game_state['player_y'] < 0:
                    self.game_state['player_y'] = 0
                    self.game_state['player_vel'] = 0
                elif self.game_state['player_y'] > self.game_params['HEIGHT'] - self.game_params['PLAYER_SIZE']:
                    self.game_state['player_y'] = self.game_params['HEIGHT'] - self.game_params['PLAYER_SIZE']
                    
                    # 检查是否在同一帧内触发了跳跃（通过键盘或姿势）
                    if key_jumped or jumped_by_pose:
                        # 跳跃触发，给一个向上的速度
                        self.game_state['player_vel'] = self.game_params['JUMP_FORCE']
                    else:
                        self.game_state['player_vel'] = 0
                    
                    # 如果不是无敌状态，则扣除生命值
                    if not self.game_state['invulnerable']:
                        self.game_state['lives'] -= 1
                        if self.game_state['lives'] > 0:
                            # 复活玩家
                            self.game_state['player_reset_pos'] = self.game_params['HEIGHT'] // 2
                            self.respawn_player()
                        else:
                            self.game_state['game_over'] = True
                
                # 生成障碍物
                self.game_state['obstacle_timer'] += delta_time
                if self.game_state['obstacle_timer'] > self.game_state['obstacle_frequency']:
                    self.spawn_obstacle()
                    self.game_state['obstacle_timer'] = 0
                
                # 更新障碍物
                for obstacle in self.game_state['obstacles'][:]:
                    obstacle['x'] -= self.game_params['OBSTACLE_SPEED']
                    
                    # 如果处于无敌状态，跳过碰撞检测
                    if self.game_state['invulnerable']:
                        continue
                    
                    # 检测碰撞
                    player_rect = pygame.Rect(
                        self.game_params['WIDTH'] // 4, 
                        self.game_state['player_y'], 
                        self.game_params['PLAYER_SIZE'], 
                        self.game_params['PLAYER_SIZE'])
                    
                    top_rect = pygame.Rect(
                        obstacle['x'], 
                        0, 
                        self.game_params['OBSTACLE_WIDTH'], 
                        obstacle['top_height'])
                    
                    bottom_rect = pygame.Rect(
                        obstacle['x'], 
                        obstacle['bottom_y'], 
                        self.game_params['OBSTACLE_WIDTH'], 
                        self.game_params['HEIGHT'] - obstacle['bottom_y'])
                    
                    if (player_rect.colliderect(top_rect) or 
                        player_rect.colliderect(bottom_rect)):
                        # 碰撞时扣除生命值
                        self.game_state['lives'] -= 1
                        
                        if self.game_state['lives'] > 0:
                            # 还有生命值，复活玩家
                            # 记录当前玩家的位置作为复活位置
                            self.game_state['player_reset_pos'] = self.game_params['HEIGHT'] // 2
                            self.respawn_player()
                        else:
                            # 生命值为0，游戏结束
                            self.game_state['game_over'] = True
                        break
                
                # 计分
                for obstacle in self.game_state['obstacles']:
                    if not obstacle['passed'] and obstacle['x'] + self.game_params['OBSTACLE_WIDTH'] < self.game_params['WIDTH'] // 4:
                        obstacle['passed'] = True
                        play_wav(f"{self.media_path}/score.mp3")
                        self.game_state['score'] += 1
                
                # 移除屏幕外的障碍物
                self.game_state['obstacles'] = [obs for obs in self.game_state['obstacles'] 
                                               if obs['x'] > -self.game_params['OBSTACLE_WIDTH']]
            
            # 绘制背景
            screen.blit(self.background_image, (0, 0))
            
            # 绘制玩家 - 无敌状态下闪烁
            player_visible = True
            if self.game_state['invulnerable']:
                # 在无敌时间内每200毫秒切换一次可见性以创建闪烁效果
                elapsed = current_time - self.game_state['invulnerable_start_time']
                if (elapsed // 200) % 2 == 0:
                    player_visible = False
            
            if player_visible:
                player_rect = pygame.Rect(
                    self.game_params['WIDTH'] // 4, 
                    self.game_state['player_y'], 
                    self.game_params['PLAYER_SIZE'], 
                    self.game_params['PLAYER_SIZE'])
                screen.blit(self.player_image, player_rect)
            
            # 绘制障碍物
            for obstacle in self.game_state['obstacles']:
                # 上方障碍物
                top_img = self.obstacle_images['top']
                top_rect = pygame.Rect(
                    obstacle['x'], 
                    0, 
                    self.game_params['OBSTACLE_WIDTH'], 
                    obstacle['top_height'])
                
                # 裁剪图像只显示需要的部分
                top_subsurface = top_img.subsurface((0, top_img.get_height() - obstacle['top_height'], 
                                                    self.game_params['OBSTACLE_WIDTH'], 
                                                    obstacle['top_height']))
                screen.blit(top_subsurface, (obstacle['x'], 0))
                
                # 下方障碍物
                bottom_img = self.obstacle_images['bottom']
                screen.blit(bottom_img, (obstacle['x'], obstacle['bottom_y']), 
                          (0, 0, self.game_params['OBSTACLE_WIDTH'], 
                           self.game_params['HEIGHT'] - obstacle['bottom_y']))
            
            # 绘制生命值（红心）
            heart_y = 20
            heart_total_width = self.game_params['LIVES'] * self.game_params['HEART_SIZE'] + (self.game_params['LIVES'] - 1) * 10
            heart_x_start = (self.game_params['WIDTH'] - heart_total_width) // 2

            for i in range(self.game_params['LIVES']):
                x_pos = heart_x_start + i * (self.game_params['HEART_SIZE'] + 10)
                # 只有当前生命值大于i时才绘制红心
                if i < self.game_state['lives']:
                    screen.blit(self.heart_image, (x_pos, heart_y))
                else:
                    # 绘制灰色心形表示失去的生命
                    screen.blit(self.heart_gray_image, (x_pos, heart_y))
            
            # 绘制分数
            font = pygame.font.SysFont(None, 48)
            score_text = font.render(f"Score: {self.game_state['score']}", True, self.game_params['SCORE_COLOR'])
            screen.blit(score_text, (20, 20))
            
            # 游戏状态提示
            if not self.game_state['game_started']:
                title_font = pygame.font.SysFont(None, 72)
                title = title_font.render("Pose Jump Game", True, self.game_params['TEXT_COLOR3'])
                subtitle = font.render("Cross jump line to JUMP!", True, self.game_params['TEXT_COLOR2'])
                start_text = font.render("Cross Jump Line or Press SPACE to Start", True, (100, 200, 255))
                
                screen.blit(title, (self.game_params['WIDTH']//2 - title.get_width()//2, self.game_params['HEIGHT']//3))
                screen.blit(subtitle, (self.game_params['WIDTH']//2 - subtitle.get_width()//2, self.game_params['HEIGHT']//2))
                screen.blit(start_text, (self.game_params['WIDTH']//2 - start_text.get_width()//2, self.game_params['HEIGHT']*2//3))
            
            if self.game_state['game_over']:
                game_over_font = pygame.font.SysFont(None, 72)
                game_over_text = game_over_font.render("Game Over", True, (255, 100, 100))
                restart_text = font.render("Cross Jump Line or Press SPACE to Restart", True, (100, 255, 100))
                final_score = font.render(f"Final Score: {self.game_state['score']}", True, self.game_params['SCORE_COLOR'])
                
                screen.blit(game_over_text, (self.game_params['WIDTH']//2 - game_over_text.get_width()//2, self.game_params['HEIGHT']//3))
                screen.blit(restart_text, (self.game_params['WIDTH']//2 - restart_text.get_width()//2, self.game_params['HEIGHT']//2))
                screen.blit(final_score, (self.game_params['WIDTH']//2 - final_score.get_width()//2, self.game_params['HEIGHT']//2 + 60))
            
            # 绘制控制提示
            controls_font = pygame.font.SysFont(None, 28)
            controls_text = controls_font.render("Pose Control: Cross jump line to JUMP", True, self.game_params['TEXT_COLOR'])
            screen.blit(controls_text, (self.game_params['WIDTH']//2 - controls_text.get_width()//2, self.game_params['HEIGHT'] - 40))
            
            # 显示当前姿势状态
            pose_color = (0, 255, 0) if "Arms detected" in self.pose_status else (200, 200, 200)
            pose_text = font.render(self.pose_status, True, pose_color)
            screen.blit(pose_text, (self.game_params['WIDTH'] - pose_text.get_width() - 20, 20))
            
            
            # 显示跳跃触发状态
            if self.jump_triggered:
                action_text = "JUMP!" if not self.game_state['game_over'] else "RESTART!"
                jump_text = font.render(action_text, True, self.game_params['ACTION_COLOR'])
                screen.blit(jump_text, (self.game_params['WIDTH'] - jump_text.get_width() - 20, 60))
            
            # 显示无敌状态
            if self.game_state['invulnerable']:
                inv_text = font.render("INVULNERABLE!", True, (255, 255, 0))
                screen.blit(inv_text, (self.game_params['WIDTH'] // 2 - inv_text.get_width() // 2, 100))
            
            # 更新显示
            pygame.display.flip()
            clock.tick(self.game_params['FPS'])
        
        pygame.quit()

    def run(self):
        # 启动线程
        self.pose_thread.start()
        self.game_thread.start()
        self.camera_window_thread.start()
        
        # 等待线程结束
        self.pose_thread.join()
        self.game_thread.join()
        self.camera_window_thread.join()
        
        rospy.loginfo("Pose Game System Shutdown")

if __name__ == '__main__':
    try:
        system = PoseGameSystem()
        system.run()
    except rospy.ROSInterruptException:
        pass