#!/usr/bin/env python3
import rospy
import cv2
import pygame
import numpy as np
import mediapipe as mp
import os
import random
import math
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

def play_wav(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

class HandSliceGame:
    def __init__(self):
        rospy.init_node('hand_slice_game')
        
        # 初始化摄像头订阅器
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/camera/color/image_raw", Image, self.image_callback)
        self.cv_image = None
        
        # 初始化手部检测
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 游戏参数
        self.blocks = []  # 存储方块 [x, y, size, speed_x, speed_y, type, color_idx]
        self.sliced_blocks = []  # 存储被切割的方块 [x, y, size, angle, rotation_speed, scale, color, timer]
        self.score = 0
        self.game_over = False
        self.last_hand_pos = None
        self.trail_points = []  # 手部轨迹点
        self.block_spawn_timer = 0
        self.game_speed = 1.0
        self.bomb_explosion = None  # 炸弹爆炸效果
        script_dir = os.path.dirname(os.path.realpath(__file__))  # 获取当前脚本所在的目录
        self.parent_dir = os.path.dirname(script_dir)  # 获取父目录
        
        # 方块类型
        self.BLOCK_NORMAL = 0
        self.BLOCK_BOMB = 1
        
        # 加载炸弹图片
        self.load_bomb_image()
        
        # 颜色定义
        self.colors = [
            (255, 0, 0),    # 蓝色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 红色
            (255, 255, 0),  # 青色
            (255, 0, 255),  # 品红
            (0, 255, 255)   # 黄色
        ]
        
        rospy.loginfo("Hand Slice Game Started! Move your hand to slice the blocks. Avoid bombs!")
    
    def load_bomb_image(self):
        """加载炸弹图片"""
        # 创建炸弹图像（如果文件不存在）
        if not os.path.exists("bomb.png"):
            self.create_bomb_image()
        
        # 加载炸弹图片 - 确保加载为4通道RGBA格式
        self.bomb_img = cv2.imread(self.parent_dir + "/media/boom.png", cv2.IMREAD_UNCHANGED)
        
        # 如果图像没有alpha通道，添加一个
        if self.bomb_img is None:
            rospy.logerr("Failed to load bomb image! Creating a placeholder.")
            self.bomb_img = self.create_placeholder_bomb()
        elif self.bomb_img.shape[2] == 3:  # 只有RGB通道
            # 添加alpha通道（全不透明）
            alpha_channel = np.ones(self.bomb_img.shape[:2], dtype=self.bomb_img.dtype) * 255
            self.bomb_img = cv2.merge((self.bomb_img[:, :, 0], 
                                     self.bomb_img[:, :, 1], 
                                     self.bomb_img[:, :, 2], 
                                     alpha_channel))
        
        rospy.loginfo(f"Bomb image loaded successfully. Shape: {self.bomb_img.shape}")
    
    def create_bomb_image(self):
        """创建炸弹图像文件（使用PNG格式保留透明度）"""
        size = 100
        bomb_img = np.zeros((size, size, 4), dtype=np.uint8)  # 4通道图像
        
        # 绘制炸弹主体（黑色）
        cv2.circle(bomb_img, (size//2, size//2), size//2 - 5, (0, 0, 0, 255), -1)
        cv2.circle(bomb_img, (size//2, size//2), size//2 - 5, (50, 50, 50, 255), 3)
        
        # 绘制引线（棕色）
        cv2.line(bomb_img, (size//2, size//2 - size//3), (size//2, size//2 - size//2 + 10), 
                (150, 75, 0, 255), 3)
        
        # 绘制火花（蓝色和橙色）
        cv2.line(bomb_img, (size//2, size//2 - size//2 + 10), 
                (size//2 + 15, size//2 - size//2 - 10), (255, 0, 0, 255), 2)
        cv2.line(bomb_img, (size//2, size//2 - size//2 + 10), 
                (size//2 - 15, size//2 - size//2 - 15), (255, 165, 0, 255), 2)
        
        # 绘制危险标志（红色感叹号）
        cv2.putText(bomb_img, "!", (size//2 - 10, size//2 + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255, 255), 3)
        
        # 保存为PNG格式以保留透明度
        cv2.imwrite("bomb.png", bomb_img)
        return bomb_img
    
    def create_placeholder_bomb(self):
        """创建替代炸弹图像（确保有alpha通道）"""
        size = 100
        bomb_img = np.zeros((size, size, 4), dtype=np.uint8)  # 4通道图像
        
        # 绘制红色三角形作为炸弹
        pts = np.array([[size//2, 10], [10, size-10], [size-10, size-10]], np.int32)
        cv2.fillPoly(bomb_img, [pts], (0, 0, 255, 255))
        
        # 添加爆炸符号
        cv2.putText(bomb_img, "BOMB", (15, size//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv2.putText(bomb_img, "X", (size//2-10, size//2+20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255, 255), 2)
        
        return bomb_img
    
    def image_callback(self, data):
        try:
            # 将ROS图像转换为OpenCV格式
            self.cv_image = cv2.flip(self.bridge.imgmsg_to_cv2(data, "bgr8"), 1)
        except CvBridgeError as e:
            rospy.logerr(e)
    
    def spawn_block(self):
        """在屏幕边缘生成一个新方块"""
        side = np.random.randint(0, 4)  # 0=上, 1=右, 2=下, 3=左
        
        size = np.random.randint(30, 60)
        speed = np.random.uniform(1.0, 3.0) * self.game_speed
        
        # 决定方块类型 (10%的概率生成炸弹)
        block_type = self.BLOCK_BOMB if random.random() < 0.1 else self.BLOCK_NORMAL
        color_idx = np.random.randint(0, len(self.colors))
        
        if side == 0:  # 上边
            x = np.random.randint(size, self.width - size)
            y = -size
            speed_x = np.random.uniform(-1.0, 1.0) * speed
            speed_y = speed
        elif side == 1:  # 右边
            x = self.width + size
            y = np.random.randint(size, self.height - size)
            speed_x = -speed
            speed_y = np.random.uniform(-1.0, 1.0) * speed
        elif side == 2:  # 下边
            x = np.random.randint(size, self.width - size)
            y = self.height + size
            speed_x = np.random.uniform(-1.0, 1.0) * speed
            speed_y = -speed
        else:  # 左边
            x = -size
            y = np.random.randint(size, self.height - size)
            speed_x = speed
            speed_y = np.random.uniform(-1.0, 1.0) * speed
        
        self.blocks.append([x, y, size, speed_x, speed_y, block_type, color_idx])

    def create_sliced_parts(self, block):
        """创建被切割方块的碎片"""
        x, y, size, _, _, block_type, color_idx = block
        color = self.colors[color_idx]
        
        # 创建两个部分（左右）
        part1 = {
            'x': x, 
            'y': y, 
            'angle': 0,  # 初始角度
            'speed_x': -5,  # 速度 (x)
            'speed_y': -2,  # 速度 (y)
            'rotation_speed': 10,  # 旋转速度 (度/帧)
            'scale': 1.0,  # 初始缩放
            'color': color,  # 颜色
            'timer': 30,  # 动画持续时间
            'size': size  # 原始尺寸
        }
        
        part2 = {
            'x': x, 
            'y': y, 
            'angle': 0,  # 初始角度
            'speed_x': 5,  # 速度 (x)
            'speed_y': 2,  # 速度 (y)
            'rotation_speed': -10,  # 旋转速度 (度/帧)
            'scale': 1.0,  # 初始缩放
            'color': color,  # 颜色
            'timer': 30,  # 动画持续时间
            'size': size  # 原始尺寸
        }
        
        return [part1, part2]
    
    def update_blocks(self):
        """更新所有方块的位置"""
        # 更新普通方块
        for block in self.blocks[:]:
            block[0] += block[3]  # x += speed_x
            block[1] += block[4]  # y += speed_y
            
            # 检查方块是否离开屏幕
            if (block[0] < -100 or block[0] > self.width + 100 or 
                block[1] < -100 or block[1] > self.height + 100):
                self.blocks.remove(block)
        
        # 更新被切割的方块
        for part in self.sliced_blocks[:]:
            # 更新位置（抛物线运动）
            part['x'] += part['speed_x']
            part['y'] += part['speed_y']
            
            # 更新旋转角度
            part['angle'] += part['rotation_speed']
            
            # 更新缩放
            part['scale'] *= 0.95  # 逐渐缩小
            
            # 更新计时器
            part['timer'] -= 1  # timer -= 1
            
            # 如果计时器结束或缩放太小，移除
            if part['timer'] <= 0 or part['scale'] < 0.1:
                self.sliced_blocks.remove(part)
    
    def draw_sliced_part(self, frame, part):
        """绘制被切割的方块部分"""
        x = part['x']
        y = part['y']
        angle = part['angle']
        scale = part['scale']
        color = part['color']
        size = part['size'] * scale  # 缩放后的尺寸
        
        # 创建旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D((0, 0), angle, 1.0)
        
        # 定义矩形的四个顶点（未旋转）
        half_size = size // 2
        pts = np.array([
            [-half_size, -half_size],
            [half_size, -half_size],
            [half_size, half_size],
            [-half_size, half_size]
        ])
        
        # 应用旋转
        rotated_pts = np.dot(pts, rotation_matrix[:, :2].T) + rotation_matrix[:, 2]
        
        # 平移顶点到正确位置
        rotated_pts += [x, y]
        
        # 转换为整数坐标
        rotated_pts = rotated_pts.astype(int)
        
        # 绘制旋转后的矩形
        cv2.fillConvexPoly(frame, rotated_pts, color)
        cv2.polylines(frame, [rotated_pts], True, (255, 255, 255), 2)
    
    def check_collision(self, start_point, end_point, frame):
        """检查手部轨迹是否切割到方块"""
        bomb_hit = False
        
        for block in self.blocks[:]:
            x, y, size, _, _, block_type, color_idx = block
            
            # 创建表示方块的四条边
            edges = [
                [(x - size, y - size), (x + size, y - size)],  # 上边
                [(x + size, y - size), (x + size, y + size)],  # 右边
                [(x + size, y + size), (x - size, y + size)],  # 下边
                [(x - size, y + size), (x - size, y - size)]   # 左边
            ]
            
            # 检查手部轨迹是否与任何一条边相交
            for edge in edges:
                if self.line_intersection(start_point, end_point, edge[0], edge[1]):
                    # 如果是炸弹，触发爆炸
                    if block_type == self.BLOCK_BOMB:
                        self.bomb_explosion = {
                            'x': x,
                            'y': y,
                            'size': size * 3,
                            'timer': 30,  # 爆炸显示时间
                            'max_size': size * 5
                        }
                        play_wav(self.parent_dir + "/media/boom.mp3")
                        self.game_over = True
                        rospy.loginfo("Bomb hit! Game over.")
                        bomb_hit = True
                        self.blocks.remove(block)
                        return bomb_hit
                    
                    # 普通方块：创建切割动画
                    sliced_parts = self.create_sliced_parts(block)
                    self.sliced_blocks.extend(sliced_parts)
                    self.blocks.remove(block)
                    play_wav(self.parent_dir + "/media/score.mp3")
                    self.score += 1
                    
                    # 增加游戏难度
                    if self.score % 2 == 0:
                        self.game_speed += 0.1
                    
                    # 在切割点绘制闪光效果
                    flash_center = ((start_point[0] + end_point[0]) // 2, 
                                   (start_point[1] + end_point[1]) // 2)
                    cv2.circle(frame, flash_center, 15, (255, 255, 255), -1)
                    
                    # 添加闪光效果到轨迹点
                    self.trail_points.append(flash_center)
                    
                    break
        
        return bomb_hit
    
    def line_intersection(self, line1_start, line1_end, line2_start, line2_end):
        """检查两条线段是否相交"""
        x1, y1 = line1_start
        x2, y2 = line1_end
        x3, y3 = line2_start
        x4, y4 = line2_end
        
        # 计算分母
        den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        
        if abs(den) < 1e-5:  # 防止除零错误
            return False
        
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        
        # 检查交点是否在两条线段上
        return 0 <= ua <= 1 and 0 <= ub <= 1
    
    def draw_block(self, frame, block):
        """绘制方块（普通方块或炸弹）"""
        x, y, size, _, _, block_type, color_idx = block
        
        if block_type == self.BLOCK_BOMB:
            # 绘制炸弹
            bomb_size = size * 2
            resized_bomb = cv2.resize(self.bomb_img, (bomb_size, bomb_size))
            
            # 确保炸弹图像有4个通道
            if resized_bomb.shape[2] == 3:
                # 添加alpha通道（全不透明）
                alpha_channel = np.ones((bomb_size, bomb_size), dtype=resized_bomb.dtype) * 255
                resized_bomb = cv2.merge((resized_bomb[:, :, 0], 
                                        resized_bomb[:, :, 1], 
                                        resized_bomb[:, :, 2], 
                                        alpha_channel))
            
            # 将炸弹图像叠加到帧上
            y1, y2 = max(0, int(y - bomb_size//2)), min(self.height, int(y + bomb_size//2))
            x1, x2 = max(0, int(x - bomb_size//2)), min(self.width, int(x + bomb_size//2))
            
            if y1 < y2 and x1 < x2:
                # 计算实际要绘制的图像部分
                bomb_h = y2 - y1
                bomb_w = x2 - x1
                
                bomb_part = resized_bomb[0:bomb_h, 0:bomb_w]
                
                # 确保bomb_part有4个通道
                if bomb_part.shape[2] == 4:
                    # 创建alpha通道
                    alpha_b = bomb_part[:, :, 3] / 255.0
                    alpha_f = 1.0 - alpha_b
                    
                    # 混合图像
                    for c in range(0, 3):
                        frame[y1:y2, x1:x2, c] = (
                            alpha_b * bomb_part[:, :, c] + 
                            alpha_f * frame[y1:y2, x1:x2, c]
                        )
                else:
                    # 如果没有alpha通道，直接覆盖
                    frame[y1:y2, x1:x2] = bomb_part[:, :, :3]
        else:
            # 绘制普通方块
            color = self.colors[color_idx]
            cv2.rectangle(frame, 
                         (int(x - size), int(y - size)),
                         (int(x + size), int(y + size)),
                         color, -1)
            cv2.rectangle(frame, 
                         (int(x - size), int(y - size)),
                         (int(x + size), int(y + size)),
                         (255, 255, 255), 2)
    
    def draw_explosion(self, frame):
        """绘制炸弹爆炸效果"""
        if self.bomb_explosion:
            x = self.bomb_explosion['x']
            y = self.bomb_explosion['y']
            size = self.bomb_explosion['size']
            
            # 绘制爆炸圆环
            cv2.circle(frame, (int(x), int(y)), int(size), (255, 0, 0), 3)
            cv2.circle(frame, (int(x), int(y)), int(size * 0.7), (0, 0, 255), 3)
            cv2.circle(frame, (int(x), int(y)), int(size * 0.4), (255, 255, 0), 3)
            
            # 绘制爆炸光线
            for i in range(8):
                angle = i * np.pi / 4
                end_x = int(x + size * np.cos(angle))
                end_y = int(y + size * np.sin(angle))
                cv2.line(frame, (int(x), int(y)), (end_x, end_y), (255, 165, 0), 3)
            
            # 更新爆炸状态
            self.bomb_explosion['size'] += 5
            self.bomb_explosion['timer'] -= 1
            
            # 如果爆炸结束，清除效果
            if self.bomb_explosion['timer'] <= 0:
                self.bomb_explosion = None
    
    def run(self):
        rate = rospy.Rate(30)  # 30Hz
        
        while not rospy.is_shutdown():
            if self.cv_image is None:
                rate.sleep()
                continue
            
            # 获取图像尺寸
            self.height, self.width, _ = self.cv_image.shape
            frame = self.cv_image.copy()
            
            # 处理手部检测
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            current_hand_pos = None
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 绘制手部关键点
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # 获取食指指尖位置（关键点8）
                    wrist = hand_landmarks.landmark[8]
                    x = int(wrist.x * self.width)
                    y = int(wrist.y * self.height)
                    current_hand_pos = (x, y)
            
            # 游戏逻辑
            if not self.game_over:
                # 更新方块位置
                self.update_blocks()
                
                # 生成新方块
                self.block_spawn_timer += 1
                if self.block_spawn_timer >= 25:  # 每25帧生成一个新方块
                    self.spawn_block()
                    self.block_spawn_timer = 0
                
                # 检测切割
                if current_hand_pos and self.last_hand_pos:
                    # 添加轨迹点
                    self.trail_points.append(current_hand_pos)
                    
                    # 限制轨迹长度
                    if len(self.trail_points) > 10:
                        self.trail_points.pop(0)
                    
                    # 检查碰撞（传入当前帧用于绘制闪光效果）
                    bomb_hit = self.check_collision(self.last_hand_pos, current_hand_pos, frame)
                    if bomb_hit:
                        self.game_over = True
                
                # 保存当前手部位置
                self.last_hand_pos = current_hand_pos
                
                # 绘制轨迹
                for i in range(1, len(self.trail_points)):
                    # 检查点是否有效
                    if self.trail_points[i-1] is not None and self.trail_points[i] is not None:
                        cv2.line(frame, self.trail_points[i-1], self.trail_points[i], (0, 255, 255), 3)
                
                # 绘制普通方块
                for block in self.blocks:
                    self.draw_block(frame, block)
                
                # 绘制被切割的方块碎片
                for part in self.sliced_blocks:
                    self.draw_sliced_part(frame, part)
                
                # 显示分数
                cv2.putText(frame, f"Score: {self.score}", (20, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 显示游戏速度
                cv2.putText(frame, f"Speed: {self.game_speed:.1f}x", (self.width - 200, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # 显示炸弹警告
                bomb_count = sum(1 for b in self.blocks if b[5] == self.BLOCK_BOMB)
                if bomb_count > 0:
                    cv2.putText(frame, f"Bombs: {bomb_count}", (self.width//2 - 60, 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                
                # 检查游戏结束条件（可选）
                if len(self.blocks) > 20:
                    self.game_over = True
            else:
                # 显示爆炸效果
                if self.bomb_explosion:
                    self.draw_explosion(frame)
                
                # 游戏结束画面
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                cv2.putText(frame, "GAME OVER", (self.width//2 - 180, self.height//2 - 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                cv2.putText(frame, "You hit a bomb!", (self.width//2 - 150, self.height//2 - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 3)
                cv2.putText(frame, f"Final Score: {self.score}", (self.width//2 - 150, self.height//2 + 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'R' to Restart", (self.width//2 - 150, self.height//2 + 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 0), 2)
            
            # 显示图像
            cv2.imshow("Hand Slice Game - Avoid Bombs!", frame)
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # 重新开始游戏
                self.blocks = []
                self.sliced_blocks = []
                self.score = 0
                self.game_over = False
                self.bomb_explosion = None
                self.game_speed = 1.0
                self.trail_points = []
            
            rate.sleep()
        
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        game = HandSliceGame()
        game.run()
    except rospy.ROSInterruptException:
        pass