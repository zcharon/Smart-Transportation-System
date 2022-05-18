"""
@Time : 2022/1/12 16:58
@Author : guanghao zhou
@File : detector.py
"""
import cv2
import torch
import numpy as np

from tracker import update_tracker
from yolov5.models.experimental import attempt_load
from yolov5.utils.general import non_max_suppression, scale_coords
from yolov5.utils.torch_utils import select_device
from yolov5.utils.datasets import letterbox


MODEL_WEIGHTS_PATH_V5 = r'yolov5/runs/train/exp/detrac.pt'
# MODEL_WEIGHTS_PATH_V5 = r'yolov5/runs/train/BiFPN/exp2/weights/best.pt'
# MODEL_WEIGHTS_PATH_V5 = r'yolov5/runs/train/yolov5s/weights/best.pt'


class BaseDet(object):
    def __init__(self):
        self.img_size = 640
        self.threshold = 0.3
        self.stride = 1

    def build_config(self):
        self.tracker = {}
        self.classes = {}
        self.location1 = {}
        self.location2 = {}
        self.frameCounter = 0
        self.recorded = []
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def feedCap(self, image, id_tracker):
        """
        调用检测器
        """
        self.frameCounter += 1
        image, _, list_bboxs, id_tracker = update_tracker(self, image, id_tracker)
        return image, list_bboxs, id_tracker

    def init_model(self):
        raise EOFError("Undefined model type.")

    def preprocess(self):
        raise EOFError("Undefined model type.")

    def detect(self):
        raise EOFError("Undefined model type.")


class DetectorV5(BaseDet):
    """
    yolov5目标检测器
    """
    def __init__(self):
        super(DetectorV5, self).__init__()
        self.init_model()
        self.build_config()

    def init_model(self):
        """
        检测模型初始化
        """
        self.weights = MODEL_WEIGHTS_PATH_V5
        self.device = '0' if torch.cuda.is_available() else 'cpu'
        self.device = select_device(self.device)
        model = attempt_load(self.weights, map_location=self.device)
        model.to(self.device).eval()
        model.half()
        # torch.save(model, 'test.pt')
        self.m = model
        self.names = model.module.names if hasattr(
            model, 'module') else model.names

    def preprocess(self, img):
        """
        待检测图像处理
        """
        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]  # 将待检测图像等比例调成规定大小，多余部分用灰色填充
        img = img[:, :, ::-1].transpose(2, 0, 1)  # 三维矩阵转置，x:0 y: 1, z: 2
        img = np.ascontiguousarray(img)  # 内存连续化
        img = torch.from_numpy(img).to(self.device)  # 将数据转入GPU
        img = img.half()  # 半精度
        img /= 255.0  # 图像归一化
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        return img0, img

    def detect(self, im):
        """
        调用检测器进行检测
        """
        im0, img = self.preprocess(im)

        pred = self.m(img, augment=False)[0]
        pred = pred.float()
        pred = non_max_suppression(pred, self.threshold, 0.4)  # NMS非极大抑制

        pred_boxes = []
        for det in pred:
            if det is not None and len(det):
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()  # 图片改大小

                for *x, conf, cls_id in det:
                    lbl = self.names[int(cls_id)]
                    if not lbl in ['car', 'van', 'bus', 'others']:
                        continue
                    x1, y1 = int(x[0]), int(x[1])
                    x2, y2 = int(x[2]), int(x[3])
                    pred_boxes.append(
                        (x1, y1, x2, y2, lbl, conf))

        return im, pred_boxes
