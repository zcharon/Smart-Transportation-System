"""
@Time : 2022/2/9 15:04
@Author : guanghao zhou
@File : call_gui.py
"""
import imutils
import cv2

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
from PyQt5.QtCore import *

from .gui import Ui_Dialog
from detector import DetectorV5
from count_car import Count


class MyMainForm(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.release_mouse = ()
        self.press_mouse = ()
        self.video_name = ""  # 被播放视频的路径
        self.frame = []  # 存图片
        self.stop_show_flag = False  # 检测是否暂停播放
        self.detect_flag = False  # 检测flag
        self.det = DetectorV5()  # 定义检查器
        self.id_tracker = {}
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器
        self.count = Count()
        # 开启视频按键
        self.open_video_btn.clicked.connect(self.open_video)
        # 关闭视频按钮
        self.stop_detect_btn.clicked.connect(self.stop_video)
        # 是否进行检测
        self.go_detect_btn.clicked.connect(self.detection)

    def __reset_parameters(self):
        """
        打开新的视频文件时，进行参数重置
        """
        self.release_mouse = ()
        self.press_mouse = ()
        self.video_name = ""  # 被播放视频的路径
        self.frame = []  # 保存图片
        self.stop_show_flag = False  # 检测是否暂停播放
        self.detect_flag = False  # 检测flag
        self.id_tracker = {}
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器

    def open_video(self):
        """
        打开视频按钮响应函数
        """
        self.__reset_parameters()
        self.video_name, _ = QFileDialog.getOpenFileName(self, "Open", "", "*.mp4;;*.avi;;All Files(*)")
        # self.video_name = 0
        if self.video_name != "":  # “”为用户取消
            self.label_head.setText("正在播放视频，请进行检测")
            self.cap = cv2.VideoCapture(self.video_name)
            self.timer_camera.start(100)
            self.timer_camera.timeout.connect(self.show_frame)

    def show_frame(self):
        """
        显示视频帧
        """
        if self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                frame = imutils.resize(frame, height=self.frame_label.size().height())
                if self.detect_flag:
                    result_im, list_bboxs, self.id_tracker = self.det.feedCap(frame, self.id_tracker)
                    # frame = imutils.resize(result_im, height=500)
                    if len(self.release_mouse) > 0 and len(self.press_mouse) > 0:
                        self.count.width = frame.shape[1]
                        self.count.height = frame.shape[0]
                        self.count.point_1 = self.press_mouse
                        self.count.point_2 = self.release_mouse
                        frame, up_count, down_count = self.count.count_car(frame, list_bboxs)
                        self.traffic_label.setText("正在进行车流量统计")
                        self.up_count_label.setText("UP:" + str(up_count))
                        self.down_count_label.setText("DOWN:" + str(down_count))

                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(frame.data, width, height, bytesPerLine,
                                 QImage.Format_RGB888).scaled(self.frame_label.width(), self.frame_label.height())
                self.frame_label.setPixmap(QPixmap.fromImage(q_image))
            else:
                self.cap.release()
                self.timer_camera.stop()  # 停止计时器

    def stop_video(self):
        """
        停止/开始显示视频
        """
        if not self.stop_show_flag:
            self.stop_show_flag = True
            self.timer_camera.stop()  # 停止计时器
            # self.cap.release()
            self.stop_detect_btn.setText("开始播放")
            self.label_head.setText("视频已停止播放")
            self.label_head.setStyleSheet("background:pink;")
        elif self.stop_show_flag:
            self.stop_show_flag = False
            self.stop_detect_btn.setText("暂停播放")
            self.timer_camera.start()
            self.label_head.setText("正在播放视频，请进行检测")
            self.label_head.setStyleSheet("background:yellow;")
            # self.timer_camera.timeout.connect(self.show_frame)
        else:
            # self.label_num.setText("Push the left upper corner button to Quit.")
            Warming = QMessageBox.warning(self, "Warming", "Push the left upper corner button to Quit.", QMessageBox.Yes)

    def detection(self):
        """
        停止/开始对播放视频进行检测
        """
        self.detect_flag = not self.detect_flag  # 取反
        if self.detect_flag:
            self.label_head.setText("已开启目标检测与跟踪网络")
            self.go_detect_btn.setText("结束检测")
            self.label_head.setStyleSheet("background: rgb(0, 255, 127)}")
        else:
            self.label_head.setText("正在播放视频，请进行检测")
            self.go_detect_btn.setText("开始检测")
            self.label_head.setStyleSheet("background:red;")

    def mousePressEvent(self, event):
        """
        鼠标单击响应函数
        """
        if self.detect_flag:
            if event.buttons() & QtCore.Qt.LeftButton:
                self.frame_label.setMouseTracking(True)
                x = event.x()
                y = event.y()
                # 鼠标过界修正
                if x < 10:
                    x = 10
                elif x > 971:
                    x = 971
                if y < 40:
                    y = 40
                elif y > 631:
                    y = 631
                self.press_mouse = (x-10, y-40)
                print(self.press_mouse)

    def mouseReleaseEvent(self, event):
        """
        鼠标单击释放响应函数
        """
        if self.detect_flag:
            x = event.x()
            y = event.y()
            # 鼠标过界修正
            if x < 10:
                x = 10
            elif x > 971:
                x = 971
            if y < 40:
                y = 40
            elif y > 631:
                y = 631
            self.release_mouse = (x-10, y-40)
            print(self.release_mouse)
            self.label_mouse_x.setText("")
            self.label_mouse_y.setText("")

    def mouseMoveEvent(self, event):
        """
        鼠标移动响应函数
        """
        mouse_track = event.windowPos()
        self.label_mouse_x.setText('X:' + str(mouse_track.x()))
        self.label_mouse_y.setText('Y:' + str(mouse_track.y()))
