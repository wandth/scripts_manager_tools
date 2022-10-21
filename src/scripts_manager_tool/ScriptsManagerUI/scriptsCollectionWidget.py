# coding=utf-8
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeView

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsTreeModel
from scripts_manager_tool.ScriptsManagerUI.util import scriptManagerModel as sql

reload(scriptsTreeModel)
reload(sql)


class ScriptsCollectionWidget(QWidget):
    def __init__(self, parent):
        super(ScriptsCollectionWidget, self).__init__(parent)
        
        # self.sql.updateScripts()
        # self.sql.addCollection("cfx")
        # self.sql.addScriptToCollection("cfx", u"测试")
        # self.sql.removeScriptFromCollection("cfx", u"测试")
        
        main_layout = QVBoxLayout(self)
        
        self.search_lineedit = QLineEdit()
        
        self.script_view = QTreeView(self)
        self.script_view.setHeaderHidden(True)
        self.script_view.setFocusPolicy(Qt.NoFocus)
        self.script_view.setSelectionMode(QTreeView.SingleSelection)
        
        self.script_model = scriptsTreeModel.ScriptsTreeModel()
        
        main_layout.addWidget(self.search_lineedit)
        main_layout.addWidget(self.script_view)
        
        self.initModel()
    
    def initModel(self):
        root = self.script_model.root()
        for collection in sql.ScriptsCollection.getScriptsCollections():
            current_collection_item = scriptsTreeModel.TreeItem(root)
            current_collection_item.setPtr(collection)
            current_collection_item.setLevel(1)
            root.appendChild(current_collection_item)
            
            for script in collection.scripts:
                current_script_item = scriptsTreeModel.TreeItem(current_collection_item)
                current_script_item.setPtr(script)
                current_script_item.setLevel(2)
                current_collection_item.appendChild(current_script_item)
        
        self.script_view.setModel(self.script_model)
