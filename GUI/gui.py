# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1124, 806)
        Dialog.setStyleSheet("")
        self.open_video_btn = QtWidgets.QPushButton(Dialog)
        self.open_video_btn.setGeometry(QtCore.QRect(1000, 40, 121, 41))
        self.open_video_btn.setStyleSheet("")
        self.open_video_btn.setObjectName("open_video_btn")
        self.go_detect_btn = QtWidgets.QPushButton(Dialog)
        self.go_detect_btn.setGeometry(QtCore.QRect(1000, 120, 121, 41))
        self.go_detect_btn.setObjectName("go_detect_btn")
        self.stop_detect_btn = QtWidgets.QPushButton(Dialog)
        self.stop_detect_btn.setGeometry(QtCore.QRect(1000, 200, 121, 41))
        self.stop_detect_btn.setObjectName("stop_detect_btn")
        self.label_head = QtWidgets.QLabel(Dialog)
        self.label_head.setGeometry(QtCore.QRect(230, 0, 491, 31))
        self.label_head.setStyleSheet("background-color: rgb(255, 255, 127);\n"
"\n"
"")
        self.label_head.setAlignment(QtCore.Qt.AlignCenter)
        self.label_head.setObjectName("label_head")
        self.frame_label = QtWidgets.QLabel(Dialog)
        self.frame_label.setEnabled(True)
        self.frame_label.setGeometry(QtCore.QRect(10, 40, 981, 631))
        self.frame_label.setMouseTracking(True)
        self.frame_label.setStyleSheet("background-color:black\n"
"")
        self.frame_label.setObjectName("frame_label")
        self.event_x = QtWidgets.QLabel(Dialog)
        self.event_x.setGeometry(QtCore.QRect(730, 0, 71, 21))
        self.event_x.setText("")
        self.event_x.setObjectName("event_x")
        self.label_mouse_x = QtWidgets.QLabel(Dialog)
        self.label_mouse_x.setGeometry(QtCore.QRect(840, 680, 72, 15))
        self.label_mouse_x.setStyleSheet("")
        self.label_mouse_x.setText("")
        self.label_mouse_x.setObjectName("label_mouse_x")
        self.label_mouse_y = QtWidgets.QLabel(Dialog)
        self.label_mouse_y.setGeometry(QtCore.QRect(920, 680, 72, 15))
        self.label_mouse_y.setStyleSheet("")
        self.label_mouse_y.setText("")
        self.label_mouse_y.setObjectName("label_mouse_y")
        self.up_count_label = QtWidgets.QLabel(Dialog)
        self.up_count_label.setGeometry(QtCore.QRect(170, 680, 51, 16))
        self.up_count_label.setStyleSheet("")
        self.up_count_label.setText("")
        self.up_count_label.setObjectName("up_count_label")
        self.down_count_label = QtWidgets.QLabel(Dialog)
        self.down_count_label.setGeometry(QtCore.QRect(230, 680, 72, 15))
        self.down_count_label.setStyleSheet("")
        self.down_count_label.setText("")
        self.down_count_label.setObjectName("down_count_label")
        self.traffic_label = QtWidgets.QLabel(Dialog)
        self.traffic_label.setGeometry(QtCore.QRect(20, 680, 141, 16))
        self.traffic_label.setStyleSheet("")
        self.traffic_label.setText("")
        self.traffic_label.setObjectName("traffic_label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.open_video_btn.setText(_translate("Dialog", "打开视频"))
        self.go_detect_btn.setText(_translate("Dialog", "开始检测"))
        self.stop_detect_btn.setText(_translate("Dialog", "停止检测"))
        self.label_head.setText(_translate("Dialog", "请选择视频进行分析"))
        self.frame_label.setText(_translate("Dialog", "请选择视频分析"))
