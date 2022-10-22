from PySide2.QtCore import QSortFilterProxyModel, QRegExp, Qt

from scripts_manager_tool.ScriptsManagerUI.modelView import scriptsListModel


class ScriptsListFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent):
        super(ScriptsListFilterProxy, self).__init__(parent)
        self.keyword = None
    
    def setFilterRegExp(self, pattern):
        if isinstance(pattern, str):
            pattern = QRegExp(pattern, Qt.CaseInsensitive,
                QRegExp.FixedString
            )
        super(ScriptsListFilterProxy, self).setFilterRegExp(pattern)
    
    def filterAcceptsRow(self, src_row, src_parent):
        src_index = self.sourceModel().index(src_row, 0, src_parent)
        src_text = self.sourceModel().data(src_index, scriptsListModel.ScriptRole.scriptNameRole)
        
        return self.filterRegExp().pattern().lower() in src_text.lower()
