# coding=utf-8
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTreeView

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsTreeModel, scriptsCollectionFilterModel
from scripts_manager_tool.ScriptsManagerUI.util import scriptManagerModel as sql

reload(scriptsTreeModel)
reload(scriptsCollectionFilterModel)
reload(sql)


class ScriptsCollectionWidget(QWidget):
    def __init__(self, parent):
        super(ScriptsCollectionWidget, self).__init__(parent)
        
        main_layout = QVBoxLayout(self)
        
        self.search_line = QLineEdit()
        
        self.scripts_collection_view = QTreeView(self)
        self.scripts_collection_view.setHeaderHidden(True)
        self.scripts_collection_view.setFocusPolicy(Qt.NoFocus)
        self.scripts_collection_view.setSelectionMode(QTreeView.SingleSelection)
        
        self.script_source_model = scriptsTreeModel.ScriptsTreeModel()
        
        self.updateModel()
        
        self.script_filter_model = scriptsCollectionFilterModel.ScriptsCollectionFilterModel()
        self.script_filter_model.setSourceModel(self.script_source_model)
        self.scripts_collection_view.setModel(self.script_filter_model)
        
        main_layout.addWidget(self.search_line)
        main_layout.addWidget(self.scripts_collection_view)
        
        self.search_line.textChanged.connect(self.search)
    
    def updateModel(self):
        root = self.script_source_model.root()
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
    
    def search(self):
        self.script_filter_model.setFilterWildcard(self.search_line.text())
