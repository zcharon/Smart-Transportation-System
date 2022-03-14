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
from behavior import get_illegal_parking, Count, get_retrograde


class MyMainForm(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.video_name = ""  # 被播放视频的路径
        self.frame = []  # 存图片
        self.det = DetectorV5()  # 定义检查器
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器
        self.count = Count()  # 定义计数器统计车流量
        self.frame_count = 0  # 视频播放帧数计数器
        self.__press_mouse = ()  # 车流量统计线起点
        self.__release_mouse = ()  # 车流量统计线终点
        self.__retrograde_press_mouse = ()  # 车辆行驶方向起点
        self.__retrograde_release_mouse = ()  # 车辆行驶方向终点
        self.__id_tracker = {}  # 全屏车辆形式轨迹字典
        self.__ill_parking_id_dirt = {}  # 车辆违停轨迹字典
        self.__retrograde_dirt = {}  # 车辆逆行轨迹字典

        self.__draw_retrograde = False  # 当前是否是绘制车辆行驶方向时间
        self.__stop_show_flag = False  # 检测是否暂停播放
        self.__detect_flag = False  # 检测flag
        self.__ill_parking_flag = False  # 判断是否进行车辆违停检测
        self.__retrograde_flag = False  # 判断是否进行车辆逆行检测

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
        # 进行车辆逆行检测
        self.btn_retrograde.clicked.connect(self.if_retrograde)

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
                if self.__detect_flag:
                    result_im, list_bboxs, self.__id_tracker = self.det.feedCap(frame, self.__id_tracker)
                    # 如果绘制了车道线，则进行车道线统计
                    if len(self.__release_mouse) > 0 and len(self.__press_mouse) > 0:
                        frame = self.__get_traffic_flow(frame, list_bboxs)
                    # 进行车辆违停检测, 每三帧检测一次，提高系统效率
                    if self.__ill_parking_flag and self.frame_count % 3 == 0:
                        self.__get_ill_parking()
                    # 进行车辆逆行检测
                    if len(self.__retrograde_press_mouse) > 0 and len(self.__retrograde_release_mouse) > 0:
                        self.__get_retrograde()
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
        if not self.__stop_show_flag:
            self.__stop_show_flag = True
            self.timer_camera.stop()  # 停止计时器
            # self.cap.release()
            self.btn_stop_detect.setText("开始播放")
            self.label_head.setText("视频已停止播放")
            self.label_head.setStyleSheet("background:pink;")
        elif self.__stop_show_flag:
            self.__stop_show_flag = False
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
        self.__detect_flag = not self.__detect_flag  # 取反
        if self.__detect_flag:
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
        if self.__detect_flag and not self.__retrograde_flag:
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
                    self.__press_mouse = (x - 10, y - 30)
                print("车流量", self.__press_mouse)
        if self.__detect_flag and self.__retrograde_flag:
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
                    self.__retrograde_press_mouse = (x - 10, y - 30)
                print("逆行", self.__retrograde_press_mouse)

    def mouseReleaseEvent(self, event):
        """
        鼠标单击释放响应函数
        """
        flag = False  # 判断鼠标点击区域是否在视频区
        if self.__detect_flag and not self.__retrograde_flag:
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
                self.__release_mouse = (x - 10, y - 30)
            print("车流量", self.__release_mouse)
            self.label_mouse_x.setText("")
            self.label_mouse_y.setText("")
        if self.__detect_flag and self.__retrograde_flag:
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
                self.__retrograde_release_mouse = (x - 10, y - 30)
                if len(self.__retrograde_press_mouse) > 0:  # 如果两次鼠标都有记录，则打开视频播放
                    self.timer_camera.start(50)
                    self.timer_camera.timeout.connect(self.show_frame)
            print("逆行", self.__retrograde_release_mouse)
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

    def if_retrograde(self):
        """
        弹窗询问是否进行车辆逆行检测
        """
        rec_code = QMessageBox.information(self, "警告", "请确保当前屏幕仅包含一条单向单行车道", QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.Yes)
        if rec_code == 65536:  # 如果取消车辆逆行检测
            print("NO")
        else:  # 如果进行车辆逆行检测
            self.timer_camera.stop()
            self.label_head.setText("请在屏幕中绘制车辆行驶方向！")
            self.__retrograde_flag = True

    def __reset_parameters(self):
        """
        打开新的视频文件时，将系统所有参数进行重置
        """
        # 初始化系统变量
        self.__release_mouse = ()
        self.__press_mouse = ()
        self.video_name = ""  # 被播放视频的路径
        self.frame = []  # 保存图片
        self.__stop_show_flag = False  # 检测是否暂停播放
        self.__detect_flag = False  # 检测flag
        self.__ill_parking_flag = False  # 检测是否有违停
        self.__id_tracker = {}
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器
        self.btn_open_video.setText("打开视频")
        self.btn_go_detect.setText("开始检测")
        self.btn_stop_detect.setText("停止检测")
        self.label_head.setText("请选择视频进行分析")
        self.label_frame.setText("请选择视频分析")

        # 提示文字清空
        self.label_ill_parking.setText("")
        self.label_traffic_detail.setText("")
        self.label_up_count.setText("")
        self.label_down_count.setText("")

        # 取消显示分割线
        self.label_line1.setText("")
        self.label_line0.setText("")

    def __get_retrograde(self):
        """
        进行车辆逆行检测
        """
        if self.__retrograde_flag:  # 打开视频播放
            self.__retrograde_flag = not self.__retrograde_flag
            self.label_head.setText("已开启目标检测与跟踪网络")
            self.label_retrograde.setText("正在进行车辆检测: \n")
        temp_dirt = {}
        if len(self.__retrograde_release_mouse) > 0 and len(self.__retrograde_press_mouse) > 0:
            self.__retrograde_dirt, temp_dirt = get_retrograde(id_tracker=self.__id_tracker,
                                                               start_point=self.__retrograde_press_mouse,
                                                               retrograde_tracker=self.__retrograde_dirt,
                                                               end_point=self.__retrograde_release_mouse)
        # --------------------------------------------------------------------------------------------------
        text_show = ""
        if len(temp_dirt) > 0:
            for key, time in temp_dirt:
                text_show += '{}: {}\n'.format(key, time)
        # ---------------------------------------------------------------------------------------------------
        self.label_retrograde.setText(self.label_retrograde.text() + text_show)

    def __conn_illegal_parking(self):
        """
        车辆违停检测按键响应函数
        """
        self.__ill_parking_flag = not self.__ill_parking_flag
        if self.__ill_parking_flag:
            self.label_ill_parking.setText("正在进行违停检测：\n")
            self.label_line1.setText("————————————————")
        else:
            self.label_ill_parking.setText("")
            self.label_line1.setText("")

    def __get_ill_parking(self):
        """
        进行车辆违停检测
        """
        id_temp, self.__ill_parking_id_dirt = get_illegal_parking(self.__id_tracker, self.__ill_parking_id_dirt)
        str_ = ''
        if len(id_temp) > 0:
            for id_, str_time in id_temp.items():
                str_ += '{} {}\n'.format(id_, str_time)
            print(self.label_ill_parking.text() + str_)
            self.label_ill_parking.setText(self.label_ill_parking.text() + str_)

    def __get_traffic_flow(self, frame, list_bboxs):
        """
        道路车流量统计
        """
        self.count.width = frame.shape[1]
        self.count.height = frame.shape[0]
        self.count.point_1 = self.__press_mouse
        self.count.point_2 = self.__release_mouse
        frame, up_count, down_count = self.count.count_car(frame, list_bboxs)
        self.label_traffic_detail.setText("正在进行交通流量统计")
        self.label_line0.setText("————————————————")
        self.label_up_count.setText("UP:" + str(up_count))
        self.label_down_count.setText("DOWN:" + str(down_count))
        return frame
