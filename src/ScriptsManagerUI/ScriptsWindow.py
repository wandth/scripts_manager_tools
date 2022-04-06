# coding=utf-8
from PySide2.QtCore import QStringListModel
from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout, QGridLayout, QLineEdit

from ScriptsManagerUI.widget import checkableTag
from ScriptsManagerUtil import sqliteHelper

reload(sqliteHelper)
reload(checkableTag)


class ScriptsWindow(QWidget) :
    def __init__(self, parent = None) :
        super(ScriptsWindow, self).__init__(parent)
        self.sql = sqliteHelper.SqliteHelper()

        main_layout = QVBoxLayout(self)
        self.tags_layout = QGridLayout()

        # tags
        tags = self.sql.getTags()
        for index, tag in enumerate(tags) :
            checked_tag = checkableTag.CheckableTag(tag, self)
            checked_tag.stateChanged.connect(self.getCheckedTags)
            self.tags_layout.addWidget(checked_tag, index % 3, index / 3)

        self.scripts_model = QStringListModel()
        self.scripts_listview = QListView()
        self.scripts_listview.setEditTriggers(QListView.NoEditTriggers)
        self.scripts_listview.setModel(self.scripts_model)

        self.search_lineedit = QLineEdit()

        main_layout.addLayout(self.tags_layout)
        main_layout.addWidget(self.search_lineedit)
        main_layout.addWidget(self.scripts_listview)

    def getCheckedTags(self) :
        checked_tags = [tag.text() for tag in self.findChildren(checkableTag.CheckableTag) if tag.isChecked()]
