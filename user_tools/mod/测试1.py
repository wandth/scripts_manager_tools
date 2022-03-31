# coding:utf8
import os
import sys
import re
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QLineEdit, QPushButton, QLabel, QProgressBar
from maya import cmds, OpenMaya as om, OpenMayaUI as omui, mel
from shiboken2 import wrapInstance
from datetime import datetime


def mayaMainWindows() :
    mainWindowsPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowsPtr), QWidget)


class MainWindows(QWidget) :
    def __init__(self, parent = mayaMainWindows()) :
        super(MainWindows, self).__init__(parent)
        main_lay = QGridLayout(self)

        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(200, 100)
        ani_repair_button = QPushButton(u"修复")

        main_lay.addWidget(QLabel(u"注意：此插件会更改为paraller\n若出现问题请切换回DG"), 0, 0, 2, 3)

        main_lay.addWidget(QLabel(u"动画组"), 3, 0, 1, 3)
        main_lay.addWidget(ani_repair_button, 4, 0, 1, 2)

        ani_repair_button.clicked.connect(aniRepair)


def aniRepair():
    for hair in cmds.ls(type = "hairSystem") :
        try:
            cmds.setAttr(hair + ".active", 0)
        except:
            continue
    for expression in cmds.ls(type = "expression") :
        if expression.startswith("xgmRefreshPreview") :
            cmds.delete(expression, e = 1)
        if re.search(r"(xgmRefreshPreview\d{0,2})", expression) :
            cmds.expression(expression, e = 1, s = "", o = "", ae = 1, uc = "none")
    mel.eval("evaluationManager -mode parallel;")


if __name__ == "__main__" :
    try :
        win_name = windows.objectName()
        if cmds.window(win_name, exists = 1) :
            windows.deleteLater()
    except :
        pass
    windows = MainWindows()
    windows.show()
