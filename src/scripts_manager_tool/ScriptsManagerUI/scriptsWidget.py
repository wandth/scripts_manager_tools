from PySide2.QtWidgets import QWidget, QLineEdit, QListView, QVBoxLayout

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsListModel
from scripts_manager_tool.ScriptsManagerUI.util import scriptManagerModel as sql

reload(sql)
reload(scriptsListModel)


class ScriptsWidget(QWidget):
    def __init__(self, parent):
        super(ScriptsWidget, self).__init__(parent)
        
        main_lay = QVBoxLayout(self)
        self.search_line = QLineEdit()
        
        self.scripts_view = QListView()
        
        self.scripts_model = scriptsListModel.ScriptsListModel([script for script in sql.Script.getScripts()])
        
        self.scripts_view.setModel(self.scripts_model)
        
        main_lay.addWidget(self.search_line)
        main_lay.addWidget(self.scripts_view)
