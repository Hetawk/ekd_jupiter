#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from pathlib import Path

import torch
import torch.backends.cudnn as cudnn
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2


package = Path(__file__).resolve().parents[1].name
print('package:', package)

workspace = Path(__file__).resolve().parents[6]
print('workspace:', workspace)

# Original catkin_ws settings: ROOT = Path(__file__).resolve().parents[6] / 'yolov5'
# weights = ROOT / 'yolov5s.pt'; data = ROOT / 'data/coco128.yaml'
# Prior EKD layout used the sibling path Path.home() / 'ekd_yolov5'.
ROOT = workspace / 'ekd_yolov5'
print('ROOT:', ROOT)
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
DEFAULT_WEIGHTS = ROOT / 'weights/safezone_best.pt'
DEFAULT_DATA = ROOT / 'data/sz-mod.yaml'


from models.common import DetectMultiBackend
from utils.general import (check_img_size, check_imshow, check_requirements,
                           non_max_suppression, print_args, scale_coords)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device
from utils.augmentations import letterbox



class Result:
    def __init__(self, xyxy=(0.0, 0.0, 0.0, 0.0), name='', conf=0.0):
        self.u1 = float(xyxy[0])
        self.v1 = float(xyxy[1])
        self.u2 = float(xyxy[2])
        self.v2 = float(xyxy[3])
        self.name = name
        self.conf = float(conf)


class Detector:

    def __init__(
        self,
        weights=DEFAULT_WEIGHTS,  # model.pt path(s)
        data=DEFAULT_DATA,  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference    ):
    ):
        check_requirements(exclude=('tensorboard', 'thop'))
        # Load model
        self.device = select_device(device)
        self.model = DetectMultiBackend(
            weights, device=self.device, dnn=dnn, data=data)
        self.stride = self.model.stride
        # self.names = self.model.names
        self.names = ['人', '自行车', '汽车', '摩托车', '飞机', '公交车', '火车', '卡车', '轮船', '交通灯',
            '消防栓', '停车标志', '停车位', '长椅', '鸟', '猫', '狗', '马', '羊', '牛',
            '大象', '熊', '斑马', '长颈鹿', '背包', '雨伞', '手提包', '领带', '行李箱', '飞盘',
            '滑雪板', '单板滑雪板', '运动球', '风筝', '棒球球棒', '棒球手套', '滑板', '冲浪板',
            '网球拍', '瓶子', '酒杯', '杯子', '叉子', '刀', '勺子', '碗', '香蕉', '苹果',
            '三明治', '橙子', '西兰花', '胡萝卜', '热狗', '披萨', '甜甜圈', '蛋糕', '椅子', '沙发',
            '盆栽植物', '床', '餐桌', '马桶', '电视', '笔记本电脑', '鼠标', '遥控器', '键盘', '手机',
            '微波炉', '烤箱', '烤面包机', '水槽', '冰箱', '书', '钟表', '花瓶', '剪刀', '泰迪熊',
            '吹风机', '牙刷']
        self.pt = self.model.pt
        self.jit = self.model.jit
        self.onnx = self.model.onnx
        self.engine = self.model.engine
        self.imgsz = check_img_size(imgsz, s=self.stride)  # check image size
        self.view_img = view_img
        self.augment = augment
        self.visualize = visualize
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.classes = classes
        self.agnostic_nms = agnostic_nms
        self.max_det = max_det
        self.line_thickness = line_thickness
        self.hide_labels = hide_labels
        self.hide_conf = hide_conf
        self.half = half

        # Half
        # FP16 supported on limited backends with CUDA
        self.half &= ((self.pt or self.jit or self.onnx or self.engine)
                      and self.device.type != 'cpu')
        if self.pt or self.jit:
            self.model.model.half() if self.half else self.model.model.float()

        # Dataloader
        self.view_img = True  # check_imshow()
        # set True to speed up constant image size inference
        cudnn.benchmark = True
        self.model.warmup(imgsz=(1, 3, *imgsz))  # warmup

    @torch.no_grad()
    def detect(self, img0):
        img = letterbox(img0, self.imgsz, stride=self.stride)[0]

        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255  # 0 - 255 to 0.0 - 1.0
        img = img[None]  # expand for batch dim

        # Inference
        pred = self.model(img, augment=self.augment, visualize=self.visualize)

        # NMS
        pred = non_max_suppression(
            pred, self.conf_thres, self.iou_thres, self.classes,
            self.agnostic_nms, max_det=self.max_det)

        det = pred[0]
        s = '%gx%g ' % img.shape[2:]  # print string
        torch.tensor(img0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        

        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(
                img.shape[2:], det[:, :4], img0.shape).round()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                # add to string
                s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "
            # Write results
            result = []
            for *xyxy, conf, cls in reversed(det):
                result.append(Result(xyxy, self.names[int(cls)], conf))
                if self.view_img:
                    c = int(cls)
                    label = None if self.hide_labels else (
                        self.names[c] if self.hide_conf else f'{self.names[c]} {conf:.2f}')

                    # 使用自定义绘图函数
                    self.cv2_box_label(img0, xyxy, label=label, color=colors(c, True))

            return img0, result
        else:
            return img0, []
        


    def cv2_box_label(self, image, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        """
        Draw bounding box and Chinese label on the image using PIL (supports Chinese).
        """
        lw = max(round(sum(image.shape) / 2 * 0.003), 2)  # line width

        p1 = (int(box[0]), int(box[1]))
        p2 = (int(box[2]), int(box[3]))

        # Draw rectangle with OpenCV
        cv2.rectangle(image, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)

        if label:
            # 将 OpenCV 图像转换为 PIL 图像
            pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            draw = ImageDraw.Draw(pil_img)

            # 使用系统字体（Ubuntu 系统中已有的中文字体）
            font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"  # 支持中文
            font_size = lw * 16  # 调整字体大小
            font = ImageFont.truetype(font_path, font_size)

            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # 调整位置
            outside = p1[1] - th >= 3
            text_origin = (p1[0], p1[1] - th - 2 if outside else p1[1] + 2)

            # 绘制背景框
            draw.rectangle([text_origin, (text_origin[0] + tw, text_origin[1] + th)], fill=color)

            # 绘制文本
            draw.text((text_origin[0], text_origin[1]), label, fill=txt_color, font=font)

            # 转回 OpenCV 图像
            image[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--weights', nargs='+', type=str, default=DEFAULT_WEIGHTS,
        help='model path(s)')
    parser.add_argument(
        '--data', type=str, default=DEFAULT_DATA,
        help='(optional) dataset.yaml path')
    parser.add_argument(
        '--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640],
        help='inference size h,w')
    parser.add_argument(
        '--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument(
        '--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument(
        '--max-det', type=int, default=1000,
        help='maximum detections per image')
    parser.add_argument(
        '--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument(
        '--view-img', action='store_true', help='show results')
    parser.add_argument(
        '--classes', nargs='+', type=int,
        help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument(
        '--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument(
        '--augment', action='store_true', help='augmented inference')
    parser.add_argument(
        '--visualize', action='store_true', help='visualize features')
    parser.add_argument(
        '--line-thickness', default=3, type=int,
        help='bounding box thickness (pixels)')
    parser.add_argument(
        '--hide-labels', default=False, action='store_true',
        help='hide labels')
    parser.add_argument(
        '--hide-conf', default=False, action='store_true',
        help='hide confidences')
    parser.add_argument(
        '--half', action='store_true',
        help='use FP16 half-precision inference')
    parser.add_argument(
        '--dnn', action='store_true',
        help='use OpenCV DNN for ONNX inference')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(vars(opt))
    return opt

