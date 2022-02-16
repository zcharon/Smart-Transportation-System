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
from behavior import get_illegal_parking


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
        self.ill_parking_id_dirt = {}
        self.frame_count = 0

        # 开启视频按键
        self.btn_open_video.clicked.connect(self.open_video)
        # 关闭视频按钮
        self.btn_stop_detect.clicked.connect(self.stop_video)
        # 是否进行检测
        self.btn_go_detect.clicked.connect(self.detection)
        # 是否进行违停检测
        self.btn_illegal_parking.clicked.connect(self.__conn_illegal_parking)
        # 下拉列表控件
        self.combox_fun.currentIndexChanged.connect(self.select_change)

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
                    # 进行车辆违停检测, 每三帧检测一次，提高系统效率
                    if self.ill_parking_flag and self.frame_count % 3 == 0:
                        self.__get_ill_parking()
                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                self.frame_count += 1
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
        flag = False  # 判断鼠标点击区域是否在视频区域
        if self.detect_flag:
            if event.buttons() & QtCore.Qt.LeftButton:
                self.label_frame.setMouseTracking(True)
                x = event.x()
                y = event.y()
                # 鼠标过界修正
                if x < 10:
                    flag = True
                elif x > 1331:
                    flag = True
                if y < 30:
                    flag = True
                elif y > 821:
                    flag = True
                if not flag:
                    self.press_mouse = (x - 10, y - 30)
                print(self.press_mouse)

    def mouseReleaseEvent(self, event):
        """
        鼠标单击释放响应函数
        """
        flag = False  # 判断鼠标点击区域是否在视频区
        if self.detect_flag:
            x = event.x()
            y = event.y()
            # 鼠标过界修正
            if x < 10:
                flag = True
            elif x > 1331:
                flag = True
            if y < 30:
                flag = True
            elif y > 821:
                flag = True
            if not flag:
                self.release_mouse = (x - 10, y - 30)
            print(self.release_mouse)
            self.label_mouse_x.setText("")
            self.label_mouse_y.setText("")

    def mouseMoveEvent(self, event):
        """
        鼠标移动响应函数
        """
        mouse_track = event.windowPos()
        if 10 < mouse_track.x() < 1331 and 30 < mouse_track.y() < 821:
            self.label_mouse_x.setText('X:' + str(mouse_track.x()))
            self.label_mouse_y.setText('Y:' + str(mouse_track.y()))

    def select_change(self, i):
        # 功能区不做任何处理
        if i == 0:
            pass
        # 清空车流量统计
        elif i == 1:
            self.count.up_count = 0
            self.count.down_count = 0
        # 清空车辆违停显示区
        elif i == 2:
            self.label_ill_parking.setText("正在进行违停检测：\n")
            self.label_line1.setText("————————————————")

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

        self.label_ill_parking.setText("")
        self.label_traffic_detail.setText("")
        self.label_up_count.setText("")
        self.label_down_count.setText("")

        self.label_line1.setText("")  # 取消分割线显示
        self.label_line0.setText("")

    def __conn_illegal_parking(self):
        """
        车辆违停检测按键响应函数
        """
        self.ill_parking_flag = not self.ill_parking_flag
        if self.ill_parking_flag:
            self.label_ill_parking.setText("正在进行违停检测：\n")
        else:
            self.label_ill_parking.setText("")

    def __get_ill_parking(self):
        """
        进行车辆违停检测
        """
        id_temp, self.ill_parking_id_dirt = get_illegal_parking(self.id_tracker, self.ill_parking_id_dirt)
        str_ = ''
        if len(id_temp) > 0:
            for id_, str_time in id_temp.items():
                str_ += '{} {}\n'.format(id_, str_time)
            print(self.label_ill_parking.text() + str_)
            self.label_ill_parking.setText(self.label_ill_parking.text() + str_)
            self.label_line1.setText("————————————————")

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
        self.label_line0.setText("————————————————")
        self.label_up_count.setText("UP:" + str(up_count))
        self.label_down_count.setText("DOWN:" + str(down_count))
        return frame
