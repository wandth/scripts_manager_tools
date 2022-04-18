# coding=utf-8
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QListView, QVBoxLayout, QGridLayout, QLineEdit, QMenu
from ScriptsManagerUI.util import ScriptsListModel, ScriptsListFilterModel, ScriptsListDelegate, delayedExecutionTimer
from ScriptsManagerUI.widget import checkableTag
from ScriptsManagerUtil import sqliteHelper

reload(sqliteHelper)
reload(checkableTag)
reload(ScriptsListModel)
reload(ScriptsListDelegate)
reload(ScriptsListFilterModel)
reload(delayedExecutionTimer)

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
        self.scripts_listview.setSelectionMode(QListView.SingleSelection)
        self.scripts_listview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scripts_listview.customContextMenuRequested.connect(self.scriptsRightClick)

        self.scripts_filter_model = ScriptsListFilterModel.ListFilterProxy()
        self.scripts_filter_model.setSourceModel(self.scripts_model)
        self.scripts_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.scripts_filter_model.setFilterKeyColumn(0)

        self.scripts_listview.setModel(self.scripts_filter_model)

        self.search_lineedit = QLineEdit()

        filter_delay = delayedExecutionTimer.DelayedExecutionTimer(parent = self.search_lineedit)
        self.search_lineedit.textChanged[str].connect(filter_delay.trigger)
        filter_delay.triggered[str].connect(lambda search_text : self.scripts_filter_model.setFilterRegExp(search_text))

        main_layout.addLayout(self.tags_layout)
        main_layout.addWidget(self.search_lineedit)
        main_layout.addWidget(self.scripts_listview)


    def setScriptsList(self) :
        checked_tags = [tag.text() for tag in self.findChildren(checkableTag.CheckableTag) if tag.isChecked()]
        scripts = []
        for tag in checked_tags :
            scripts.extend(self.sql.queryScriptsFromTag(tag))
        self.scripts_model.setNewData(scripts)

    def scriptsRightClick(self, pos) :
        table_menu = QMenu(self)
        select_all_action = table_menu.addAction(u"管理收藏")

        table_menu.popup(self.scripts_listview.viewport().mapToGlobal(pos))
        select_all_action.triggered.connect(self.popupTagEditorMenu)

    def popupTagEditorMenu(self):
        selection = self.scripts_listview.selectedIndexes()
        print selection