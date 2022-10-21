# coding=utf-8
import os
import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QWidget, QPushButton, QApplication, QListWidget, QStackedWidget
from maya import OpenMayaUI as omui, cmds, mel
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance

from scripts_manager_tool.ScriptsManagerUI import scriptsCollectionWidget, scriptsWidget

reload(scriptsCollectionWidget)
reload(scriptsWidget)


def mayaMainWindows():
    return wrapInstance(long(omui.MQtUtil.mainWindow()), QWidget)


class MainWindow(MayaQWidgetDockableMixin, QWidget):
    object_name = "scripts_manager_tools"
    docker_windows_name = object_name + "Dock"
    windows_title = "Scripts Manager"
    
    def __init__(self, parent=mayaMainWindows()):
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(300, 600)
        self.setObjectName(self.object_name)
        self.setWindowTitle(self.windows_title)
        
        main_layout = QHBoxLayout(self)
        self.menus = QListWidget()
        
        self.stack_widget = QStackedWidget()
        # 三个页面
        
        # 脚本页面  ----> 有分类
        self.menus.insertItem(0, u"分类")
        self.scripts_collection_widget = scriptsCollectionWidget.ScriptsCollectionWidget(self)
        
        # 脚本页面  ----> 无分类
        self.menus.insertItem(1, u"脚本")
        self.scrips_widget = scriptsWidget.ScriptsWidget(self)
        
        # 脚本页面  ----> 个人收藏
        self.menus.insertItem(2, u"收藏")
        self.user_glad_widget = QWidget()
        
        self.stack_widget.addWidget(self.scripts_collection_widget)
        self.stack_widget.addWidget(self.scrips_widget)
        self.stack_widget.addWidget(self.user_glad_widget)
        
        main_layout.addWidget(self.menus)
        main_layout.addWidget(self.stack_widget)
        
        self.menus.currentRowChanged.connect(self.changeWidget)
    
    def changeWidget(self, index):
        self.stack_widget.setCurrentIndex(index)
    
    def setWindowDocked(self):
        cmds.workspaceControl(self.docker_windows_name, initialWidth=300, widthProperty='preferred', minimumWidth=300, visible=True,
            label=self.windows_title
        )
        cmds.workspaceControl(self.docker_windows_name, r=True, ttc=["AttributeEditor", -1], collapse=False, e=True)
        cmds.control(self.object_name, parent=self.docker_windows_name, e=True)
    
    @classmethod
    def deleteThisWindow(cls):
        [widget.close() and widget.deleteLater() for widget in QApplication.allWidgets() if widget.objectName() == cls.object_name]
    
    @classmethod
    def deleteWindowAndDock(cls):
        [widget.close() and widget.deleteLater() for widget in QApplication.allWidgets() if widget.objectName() == cls.object_name]
        try:
            [cmds.deleteUI(widget.objectName()) for widget in QApplication.allWidgets() if widget.objectName() == cls.docker_windows_name]
        except:
            pass


def addThirdPath():
    module_path = cmds.moduleInfo(moduleName="scripts_manager_tools", p=1)
    
    [sys.path.append(third_lib_path) for third_lib_path in [
        os.path.join(module_path, "third_lib").replace('\\', '/'),
        os.path.join(module_path, "src").replace('\\', '/')
    ] if third_lib_path not in sys.path]
    
    # todo: 添加 plugin path


def createScriptsManagerWindow():
    MainWindow.deleteWindowAndDock()
    window = MainWindow()
    window.show()
    window.setWindowDocked()


def createToolButton():
    # 注意 此 button只需要添加一次即可
    status_line = mel.eval('global string $gStatusLine;$temp = $gStatusLine;')
    button_parent_name = status_line.split('|')[-1]
    parent_widget = [widget for widget in QApplication.allWidgets() if widget.objectName() == button_parent_name][0]
    
    create_tool_button = QPushButton(parent_widget)
    create_tool_button.setText(u"工具架")
    create_tool_button.setObjectName("create_scripts_manager_tools_button")
    
    parent_widget.layout().addWidget(create_tool_button)
    create_tool_button.clicked.connect(createScriptsManagerWindow)
