import argparse
import datetime
import threading
import time
from pathlib import Path
from app.constants import Constants
from app.database.database import SessionLocal
from app.database.models import Notification

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import numpy as np
from app.telegram_utils import send_telegram
from models.experimental import attempt_load
from utils.datasets import LoadImages, LoadStreams, letterbox
from utils.general import (apply_classifier, check_img_size, check_imshow,
                           check_requirements, increment_path,
                           non_max_suppression, scale_coords, set_logging,
                           strip_optimizer, xyxy2xywh)
from utils.plots import plot_one_box
from utils.torch_utils import (TracedModel, load_classifier, select_device,
                               time_synchronized)
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder

import requests
PARENT_PATH = os.getcwd()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class YoloDetect():
    def __init__(self):
        self.alert_telegram_each = 60  # seconds
        self.last_alert = None
        self.conf_thres = 0.75
        self.iou_thres = 0.5
        self.augment = None
        self.weights, self.imgsz, self.trace = 'weights/one_label.pt', 640, not False

        self.device = select_device('cpu')
        self.half = self.device.type != 'cpu'

        self.model = attempt_load(
            self.weights, map_location=self.device)
        self.stride = int(self.model.stride.max())
        self.imgsz = check_img_size(
            self.imgsz, s=self.stride)

        if self.trace:
            self.model = TracedModel(self.model, self.device, self.imgsz)

        if self.half:
            self.model.half()

    def alert(self, img):
        if (self.last_alert is None) or (
                (datetime.datetime.utcnow() - self.last_alert).total_seconds() > self.alert_telegram_each):
            self.last_alert = datetime.datetime.utcnow()
            file_name = str(int(datetime.datetime.timestamp(
                datetime.datetime.now()))) + '.jpg'
            save_path = os.path.join(PARENT_PATH, Constants.PUBLIC_FOLDER +
                                     file_name)
            cv2.imwrite(save_path, img)
            thread = threading.Thread(target=send_telegram, args=[save_path])
            multipart_data = MultipartEncoder(
                fields={
                    'file': (file_name, open(save_path, 'rb'))
                }
            )
            try:
                response = requests.post('http://localhost:8008/backend/api/notification',
                                     data=multipart_data, headers={'Content-Type': multipart_data.content_type})
            except Exception as e:
                pass
            thread.start()
        return img

    def detect_image(self, img):
        img0 = img
        img = letterbox(img, self.imgsz, self.stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        names = self.model.module.names if hasattr(
            self.model, 'module') else self.model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(
                next(self.model.parameters())))  # run once
        old_img_w = old_img_h = self.imgsz
        old_img_b = 1

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()
        img /= 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        if self.device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                self.model(img, augment=self.augment)[0]

        pred = self.model(img, augment=self.augment)[0]

        pred = non_max_suppression(
            pred, self.conf_thres, self.iou_thres)

        for i, det in enumerate(pred):
            im0 = img0

            if len(det):
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], im0.shape).round()

                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label,
                                 color=colors[int(cls)], line_thickness=3)
        self.alert(im0)
        return im0, len(det) > 0


if __name__ == '__main__':
    _model = YoloDetect()
    img = cv2.imread('./image1664298066486.jpg')
    im0, _ = _model.detect_image(img)
    cv2.imshow("", img)
    cv2.waitKey(0)
