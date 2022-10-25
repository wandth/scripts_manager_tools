# coding=utf-8
import sys

from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QWidget, QLineEdit, QListView, QVBoxLayout, QMenu
from maya import mel

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsListModel, scriptsListFilterModel, scriptsTreeModel
from scripts_manager_tool.ScriptsManagerUI.util import scriptManagerModel as sql

reload(sql)
reload(scriptsListModel)
reload(scriptsTreeModel)


class ScriptsWidget(QWidget):
    def __init__(self, parent):
        super(ScriptsWidget, self).__init__(parent)
        
        main_lay = QVBoxLayout(self)
        self.search_line = QLineEdit()
        
        self.scripts_view = QListView()
        self.scripts_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scripts_view.doubleClicked.connect(self.executeScript)
        self.scripts_view.customContextMenuRequested.connect(self.scriptRightClickMenu)
        
        self.scripts_source_model = scriptsListModel.ScriptsListModel([script for script in sql.Script.getScripts()])
        
        self.scripts_filter_model = scriptsListFilterModel.ScriptsListFilterProxy(self)
        self.scripts_filter_model.setSourceModel(self.scripts_source_model)
        
        self.scripts_view.setModel(self.scripts_filter_model)
        
        main_lay.addWidget(self.search_line)
        main_lay.addWidget(self.scripts_view)
        
        self.search_line.textChanged.connect(self.search)
    
    def scriptRightClickMenu(self, pos):
        listview_menu = QMenu(self)
        
        execute_script = listview_menu.addAction(u"运行")
        listview_menu.addSeparator()
        
        edit_script_collection = listview_menu.addAction(u"编辑分类")
        edit_script_collection.triggered.connect(self.editCollectionWidget)
        execute_script.triggered.connect(self.executeScript)
        
        listview_menu.exec_(QCursor.pos())
    
    def executeScript(self, *args):
        select_indexes = self.scripts_view.selectionModel().selectedIndexes()
        if not select_indexes:
            return
        select_index = select_indexes[0]
        script_name = select_index.data(scriptsTreeModel.ScriptRole.scriptNameRole)
        script_type = select_index.data(scriptsTreeModel.ScriptRole.scriptTypeRole)
        script_path = select_index.data(scriptsTreeModel.ScriptRole.scriptPathRole)
        script_module_path = select_index.data(scriptsTreeModel.ScriptRole.scriptModulePathRole)
        
        script_type_str = ""
        if script_type == sql.ScriptType.mel_type:
            mel.eval(u"""source "{mel_script}";""".format(mel_script=unicode(script_path)))
            script_type_str = "mel"
        elif script_type == sql.ScriptType.python_script_type:
            execfile(script_path)
            script_type_str = "python script"
        elif script_type == sql.ScriptType.python_module_type:
            [sys.path.append(path) for path in [
                script_module_path
            ] if path not in sys.path]
            execfile(script_path)
            script_type_str = "python module"
        print(u"\n exec --> {name} --> {script_type} --> {script_path}".format(
            name=script_name,
            script_type=script_type_str,
            script_path=script_path
        ))
    
    def search(self):
        self.scripts_filter_model.setFilterWildcard(self.search_line.text())
    
    def editCollectionWidget(self):
        pass
