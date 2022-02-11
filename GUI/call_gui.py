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
from behavior import Behavior


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
        self.ill_parking_flag = False
        self.det = DetectorV5()  # 定义检查器
        self.id_tracker = {}
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器
        self.count = Count()  # 定义计数器统计车流量
        self.behavior = Behavior()

        # 开启视频按键
        self.btn_open_video.clicked.connect(self.open_video)
        # 关闭视频按钮
        self.btn_stop_detect.clicked.connect(self.stop_video)
        # 是否进行检测
        self.btn_go_detect.clicked.connect(self.detection)
        # 是否进行违停检测
        self.btn_illegal_parking.clicked.connect(self.__get_illegal_parking)

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
            self.timer_camera.start(50)
            self.timer_camera.timeout.connect(self.show_frame)

    def show_frame(self):
        """
        显示视频帧
        """
        if self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                frame = imutils.resize(frame, height=self.label_frame.size().height())
                if self.detect_flag:
                    result_im, list_bboxs, self.id_tracker = self.det.feedCap(frame, self.id_tracker)
                    # 如果绘制了车道线，则进行车道线统计
                    if len(self.release_mouse) > 0 and len(self.press_mouse) > 0:
                        frame = self.__get_traffic_flow(frame, list_bboxs)
                    if self.ill_parking_flag:
                        self.behavior.get_illegal_parking(self.id_tracker)
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(frame.data, width, height, bytesPerLine,
                                 QImage.Format_RGB888).scaled(self.label_frame.width(), self.label_frame.height())
                self.label_frame.setPixmap(QPixmap.fromImage(q_image))
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
            self.btn_stop_detect.setText("开始播放")
            self.label_head.setText("视频已停止播放")
            self.label_head.setStyleSheet("background:pink;")
        elif self.stop_show_flag:
            self.stop_show_flag = False
            self.btn_stop_detect.setText("暂停播放")
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
            self.btn_go_detect.setText("结束检测")
            self.label_head.setStyleSheet("background: rgb(0, 255, 127)}")
        else:
            self.label_head.setText("正在播放视频，请进行检测")
            self.btn_go_detect.setText("开始检测")
            self.label_head.setStyleSheet("background:red;")

    def mousePressEvent(self, event):
        """
        鼠标单击响应函数
        """
        if self.detect_flag:
            if event.buttons() & QtCore.Qt.LeftButton:
                self.label_frame.setMouseTracking(True)
                x = event.x()
                y = event.y()
                # 鼠标过界修正
                if x < 10:
                    x = 10
                elif x > 1331:
                    x = 1331
                if y < 30:
                    y = 30
                elif y > 821:
                    y = 821
                self.press_mouse = (x-10, y-30)
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
            elif x > 1331:
                x = 1331
            if y < 30:
                y = 30
            elif y > 821:
                y = 821
            self.release_mouse = (x-10, y-30)
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
        self.ill_parking_flag = False  # 检测是否有违停
        self.id_tracker = {}
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器
        self.btn_open_video.setText("打开视频")
        self.btn_go_detect.setText("开始检测")
        self.btn_stop_detect.setText("停止检测")
        self.label_head.setText("请选择视频进行分析")
        self.label_frame.setText("请选择视频分析")
        self.label_frame_size.setText("视频尺寸")

        self.label_traffic_detail.setText("")
        self.label_up_count.setText("")
        self.label_down_count.setText("")

    def __get_illegal_parking(self):
        """
        进行车辆违停检测
        """
        self.ill_parking_flag = not self.ill_parking_flag

    def __get_traffic_flow(self, frame, list_bboxs):
        """
        道路车流量统计
        """
        self.count.width = frame.shape[1]
        self.count.height = frame.shape[0]
        self.count.point_1 = self.press_mouse
        self.count.point_2 = self.release_mouse
        frame, up_count, down_count = self.count.count_car(frame, list_bboxs)
        self.label_traffic_detail.setText("正在进行车流量统计")
        self.label_up_count.setText("UP:" + str(up_count))
        self.label_down_count.setText("DOWN:" + str(down_count))
        return frame
