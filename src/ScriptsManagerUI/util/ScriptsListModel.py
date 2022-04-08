from PySide2.QtCore import Qt, QAbstractListModel

from ScriptsManagerUI.util import ScriptRole

reload(ScriptRole)


class ScriptsListModel(QAbstractListModel) :
    def __init__(self, data, parent = None) :
        super(ScriptsListModel, self).__init__(parent)
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
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
