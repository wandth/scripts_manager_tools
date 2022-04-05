# coding=utf-8
import os
import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QWidget, QPushButton, QApplication, QTabWidget
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui, cmds, mel
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from ScriptsManagerUI import ScriptsWindow

reload(ScriptsWindow)


def mayaMainWindows() :
    return wrapInstance(long(omui.MQtUtil.mainWindow()), QWidget)


class MainWindow(MayaQWidgetDockableMixin, QWidget) :
    object_name = "scripts_manager_tools"
    docker_windows_name = object_name + "Dock"
    windows_title = "Scripts Manager"

    def __init__(self, parent = mayaMainWindows()) :
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(300, 600)
        self.setObjectName(self.object_name)
        self.setWindowTitle(self.windows_title)

        main_layout = QHBoxLayout(self)

        tab_widget = QTabWidget()
        self.scripts_tab = ScriptsWindow.ScriptsWindow(self)

        tab_widget.addTab(self.scripts_tab, "Scripts")

        main_layout.addWidget(tab_widget)

    def setWindowDocked(self) :
        cmds.workspaceControl(self.docker_windows_name, initialWidth = 300, widthProperty = 'preferred', minimumWidth = 300, visible = True,
                              label = self.windows_title)
        cmds.workspaceControl(self.docker_windows_name, r = True, ttc = ["AttributeEditor", -1], collapse = False, e = True)
        cmds.control(self.object_name, parent = self.docker_windows_name, e = True)

    @classmethod
    def deleteThisWindow(cls) :
        [widget.close() and widget.deleteLater() for widget in QApplication.allWidgets() if widget.objectName() == cls.object_name]

    @classmethod
    def deleteWindowAndDock(cls) :
        [widget.close() and widget.deleteLater() for widget in QApplication.allWidgets() if widget.objectName() == cls.object_name]
        try :
            [cmds.deleteUI(widget.objectName()) for widget in QApplication.allWidgets() if widget.objectName() == cls.docker_windows_name]
        except :
            pass


def addThirdLibToSysPath() :
    module_path = os.path.dirname(os.path.dirname(__file__))

    [sys.path.append(third_lib_path) for third_lib_path in [
        os.path.join(module_path, "third_libs").replace('\\', '/'),
        os.path.join(module_path, "src").replace('\\', '/')
    ] if third_lib_path not in sys.path]


def createScriptsManagerWindow() :
    MainWindow.deleteWindowAndDock()
    window = MainWindow()
    window.show()
    window.setWindowDocked()


def createToolButton() :
    # 注意 此 button只需要添加一次即可
    status_line = mel.eval('global string $gStatusLine;$temp = $gStatusLine;')
    button_parent_name = status_line.split('|')[-1]
    parent_widget = [widget for widget in QApplication.allWidgets() if widget.objectName() == button_parent_name][0]

    create_tool_button = QPushButton(parent_widget)
    create_tool_button.setText(u"工具架")
    create_tool_button.setObjectName("create_scripts_manager_tools_button")

    parent_widget.layout().addWidget(create_tool_button)
    create_tool_button.clicked.connect(createScriptsManagerWindow)
