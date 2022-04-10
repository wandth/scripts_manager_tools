# coding=utf-8
from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout, QGridLayout, QLineEdit
from ScriptsManagerUI.util import ScriptsListModel, ScriptsListFilterModel, ScriptsListDelegate

from ScriptsManagerUI.widget import checkableTag
from ScriptsManagerUtil import sqliteHelper

reload(sqliteHelper)
reload(checkableTag)
reload(ScriptsListModel)
reload(ScriptsListDelegate)
reload(ScriptsListFilterModel)


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
            checked_tag.stateChanged.connect(self.setScriptsList)
            self.tags_layout.addWidget(checked_tag, index % 3, index / 3)

        self.scripts_model = ScriptsListModel.ScriptsListModel()

        self.scripts_listview = QListView()
        self.scripts_listview.setItemDelegate(ScriptsListDelegate.ScriptsListDelegate())
        self.scripts_listview.setModel(self.scripts_model)

        self.search_lineedit = QLineEdit()

        main_layout.addLayout(self.tags_layout)
        main_layout.addWidget(self.search_lineedit)
        main_layout.addWidget(self.scripts_listview)

    def setScriptsList(self) :
        checked_tags = [tag.text() for tag in self.findChildren(checkableTag.CheckableTag) if tag.isChecked()]
        scripts = []
        for tag in checked_tags :
            scripts.extend(self.sql.queryScriptsFromTag(tag))
        self.scripts_model.setNewData(scripts)
