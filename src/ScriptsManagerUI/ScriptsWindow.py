# coding=utf-8
from PySide2.QtCore import QStringListModel
from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QListView

from ScriptsManagerUtil import sqliteHelper


class ScriptsWindow(QWidget) :
    def __init__(self, parent = None) :
        super(ScriptsWindow, self).__init__(parent)

        main_layout = QHBoxLayout(self)

        self.scripts_model = QStringListModel()
        self.scripts_listview = QListView()

        self.scripts_listview.setModel(self.scripts_model)

        main_layout.addWidget(self.scripts_listview)

        self.scripts_model.setStringList(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])