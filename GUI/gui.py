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
        self.open_video_btn = QtWidgets.QPushButton(Dialog)
        self.open_video_btn.setGeometry(QtCore.QRect(950, 110, 121, 41))
        self.open_video_btn.setStyleSheet("")
        self.open_video_btn.setObjectName("open_video_btn")
        self.go_detect_btn = QtWidgets.QPushButton(Dialog)
        self.go_detect_btn.setGeometry(QtCore.QRect(950, 190, 121, 41))
        self.go_detect_btn.setObjectName("go_detect_btn")
        self.stop_detect_btn = QtWidgets.QPushButton(Dialog)
        self.stop_detect_btn.setGeometry(QtCore.QRect(950, 270, 121, 41))
        self.stop_detect_btn.setObjectName("stop_detect_btn")
        self.label_head = QtWidgets.QLabel(Dialog)
        self.label_head.setGeometry(QtCore.QRect(250, 40, 511, 31))
        self.label_head.setStyleSheet("background-color: rgb(255, 255, 127);\n"
"\n"
"")
        self.label_head.setAlignment(QtCore.Qt.AlignCenter)
        self.label_head.setObjectName("label_head")
        self.frame_label = QtWidgets.QLabel(Dialog)
        self.frame_label.setEnabled(True)
        self.frame_label.setGeometry(QtCore.QRect(70, 100, 801, 501))
        self.frame_label.setMouseTracking(True)
        self.frame_label.setStyleSheet("background-color:black\n"
"")
        self.frame_label.setObjectName("frame_label")
        self.event_x = QtWidgets.QLabel(Dialog)
        self.event_x.setGeometry(QtCore.QRect(780, 40, 71, 21))
        self.event_x.setText("")
        self.event_x.setObjectName("event_x")
        self.label_mouse_x = QtWidgets.QLabel(Dialog)
        self.label_mouse_x.setGeometry(QtCore.QRect(740, 630, 72, 15))
        self.label_mouse_x.setText("")
        self.label_mouse_x.setObjectName("label_mouse_x")
        self.label_mouse_y = QtWidgets.QLabel(Dialog)
        self.label_mouse_y.setGeometry(QtCore.QRect(820, 630, 72, 15))
        self.label_mouse_y.setText("")
        self.label_mouse_y.setObjectName("label_mouse_y")

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
