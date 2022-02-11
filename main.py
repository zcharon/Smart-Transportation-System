"""
@Time : 2022/2/9 16:42
@Author : guanghao zhou
@File : main.py
"""
import sys
from GUI.call_gui import MyMainForm
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    myWin = MyMainForm()
    # 将窗口控件显示在屏幕上
    myWin.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
