from PySide2.QtCore import Qt, QAbstractListModel

from scripts_manager_tool.ScriptsManagerUI.modelView import ScriptRole

reload(ScriptRole)


class ScriptsListModel(QAbstractListModel) :
    def __init__(self, data = None, parent = None) :
        super(ScriptsListModel, self).__init__(parent)
        if data is None :
            data = []
        self._data = data

    def rowCount(self, parent) :
        return len(self._data)

    def data(self, index, role) :
        if not index.isValid() :
            return None

        row = index.row()
        if role == ScriptRole.ScriptRole.scriptNameRole :
            value = self._data[row][0]
            return value
        if role == ScriptRole.ScriptRole.scriptPathRole :
            value = self._data[row][1]
            return value
        if role == ScriptRole.ScriptRole.scriptTypeRole :
            value = self._data[row][2]
            return value
        if role == ScriptRole.ScriptRole.scriptPythonTypeRole :
            value = self._data[row][3]
            return value
        if role == ScriptRole.ScriptRole.scriptTagRole :
            value = self._data[row][4]
            return value

    def flags(self, index) :
        if index.isValid() :
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setNewData(self, data) :
        self.beginResetModel()
        self._data = data
        self.endResetModel()
