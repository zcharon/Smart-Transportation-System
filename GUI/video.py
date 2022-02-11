"""
@Time : 2022/2/9 14:19
@Author : guanghao zhou
@File : video.py
"""
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


import cv2
from PyQt5.QtCore import QTimer


class Video(QWidget):
    def __init__(self):
        super(Video, self).__init__()
        self.frame = []  # 存图片
        self.detectFlag = False  # 检测flag
        self.cap = []
        self.timer_camera = QTimer()  # 定义定时器

        # 外框
        self.resize(900, 650)
        self.setWindowTitle("Head Detection")
        # 图片label
        self.label = QLabel(self)
        self.label.setText("Waiting for video...")
        self.label.setFixedSize(800, 450)  # width height
        self.label.move(50, 100)
        self.label.setStyleSheet("QLabel{background:pink;}"
                                 "QLabel{color:rgb(100,100,100);font-size:15px;font-weight:bold;font-family:宋体;}"
                                 )
        # 显示人数label
        self.label_num = QLabel(self)
        self.label_num.setText("Waiting for detectiong...")
        self.label_num.setFixedSize(430, 40)  # width height
        self.label_num.move(200, 20)
        self.label_num.setStyleSheet("QLabel{background:yellow;}")
        # 开启视频按键
        self.btn = QPushButton(self)
        self.btn.setText("Open")
        self.btn.move(150, 570)
        self.btn.clicked.connect(self.slotStart)
        # 检测按键
        self.btn_detect = QPushButton(self)
        self.btn_detect.setText("Detect")
        self.btn_detect.move(400, 570)
        self.btn_detect.setStyleSheet("QPushButton{background:red;}")  # 没检测红色，检测绿色
        self.btn_detect.clicked.connect(self.detection)
        # 关闭视频按钮
        self.btn_stop = QPushButton(self)
        self.btn_stop.setText("Stop")
        self.btn_stop.move(700, 570)
        self.btn_stop.clicked.connect(self.slotStop)

    def slotStart(self):
        """ Slot function to start the progamme
            """
        videoName, _ = QFileDialog.getOpenFileName(self, "Open", "", "*.mp4;;*.avi;;All Files(*)")
        if videoName != "":  # “”为用户取消
            self.cap = cv2.VideoCapture(videoName)
            self.timer_camera.start(100)
            self.timer_camera.timeout.connect(self.openFrame)

    def slotStop(self):
        """ Slot function to stop the programme
            """
        if self.cap != []:
            self.cap.release()
            self.timer_camera.stop()  # 停止计时器
            self.label.setText("This video has been stopped.")
            self.label.setStyleSheet("QLabel{background:pink;}"
                                     "QLabel{color:rgb(100,100,100);font-size:15px;font-weight:bold;font-family:宋体;}"
                                     )
        else:
            self.label_num.setText("Push the left upper corner button to Quit.")
            Warming = QMessageBox.warning(self, "Warming", "Push the left upper corner button to Quit.", QMessageBox.Yes)

    def openFrame(self):
        """ Slot function to capture frame and process it
            """

        if (self.cap.isOpened()):
            ret, self.frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                if self.detectFlag == True:
                    # 检测代码self.frame
                    self.label_num.setText("There are " + str(5) + " people.")

                height, width, bytesPerComponent = frame.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(frame.data, width, height, bytesPerLine,
                                 QImage.Format_RGB888).scaled(self.label.width(), self.label.height())
                self.label.setPixmap(QPixmap.fromImage(q_image))
            else:
                self.cap.release()
                self.timer_camera.stop()  # 停止计时器

    def detection(self):
        self.detectFlag = not self.detectFlag  # 取反
        if self.detectFlag == True:
            self.btn_detect.setStyleSheet("QPushButton{background:green;}")
        else:
            self.btn_detect.setStyleSheet("QPushButton{background:red;}")
    #        self.label_num.setText("There are 5 people.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my = Video()
    my.show()
    sys.exit(app.exec_())