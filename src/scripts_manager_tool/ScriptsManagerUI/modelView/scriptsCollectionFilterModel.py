from PySide2.QtCore import QSortFilterProxyModel, QRegExp, Qt

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsTreeModel

reload(scriptsTreeModel)


class ScriptsCollectionFilterModel(QSortFilterProxyModel):
    def __init__(self):
        super(ScriptsCollectionFilterModel, self).__init__()
    
    def setFilterRegExp(self, pattern):
        if isinstance(pattern, str):
            pattern = QRegExp(
                pattern, Qt.CaseInsensitive,
                QRegExp.FixedString
            )
        super(ScriptsCollectionFilterModel, self).setFilterRegExp(pattern)
    
    def _accept_index(self, idx):
        if idx.isValid():
            text = idx.data(scriptsTreeModel.ScriptRole.scriptNameRole)
            if self.filterRegExp().indexIn(text) >= 0:
                return True
            for row in range(idx.model().rowCount(idx)):
                if self._accept_index(idx.model().index(row, 0, idx)):
                    return True
        return False
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        return self._accept_index(idx)
