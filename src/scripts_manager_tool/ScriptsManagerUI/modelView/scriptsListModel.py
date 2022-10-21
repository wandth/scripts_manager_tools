from PySide2.QtCore import Qt, QAbstractListModel

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsTreeModel

reload(scriptsTreeModel)


class ScriptsListModel(QAbstractListModel):
    def __init__(self, data=None, parent=None):
        super(ScriptsListModel, self).__init__(parent)
        if data is None:
            data = []
        self._data = data
    
    def rowCount(self, parent):
        return len(self._data)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        row = index.row()
        if role == Qt.DisplayRole or role == scriptsTreeModel.ScriptRole.scriptNameRole:
            value = self._data[row].name
            return value
        if role == scriptsTreeModel.ScriptRole.scriptPathRole:
            value = self._data[row].script_path
            return value
        if role == scriptsTreeModel.ScriptRole.scriptTypeRole:
            value = self._data[row].script_type
            return value
        if role == scriptsTreeModel.ScriptRole.scriptModulePathRole:
            value = self._data[row].script_module_path
            return value
        return None
    
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def updateDatas(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()
