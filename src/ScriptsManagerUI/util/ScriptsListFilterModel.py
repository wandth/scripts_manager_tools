from PySide2.QtCore import QSortFilterProxyModel, QRegExp, Qt
from ScriptsManagerUI.util import ScriptRole

reload(ScriptRole)


class ListFilterProxy(QSortFilterProxyModel) :
    def __init__(self) :
        super(ListFilterProxy, self).__init__()
        self.keyword = None

    def setFilterRegExp(self, pattern) :
        if isinstance(pattern, str) :
            pattern = QRegExp(pattern, Qt.CaseInsensitive,QRegExp.FixedString)
        super(ListFilterProxy, self).setFilterRegExp(pattern)

    def filterAcceptsRow(self, src_row, src_parent) :
        src_index = self.sourceModel().index(src_row, 0, src_parent)
        src_text = self.sourceModel().data(src_index, ScriptRole.ScriptRole.scriptNameRole)

        lower_text =  self.filterRegExp().pattern().lower()
        decode_src_text =  src_text.decode('utf-8')

        return lower_text in decode_src_text
