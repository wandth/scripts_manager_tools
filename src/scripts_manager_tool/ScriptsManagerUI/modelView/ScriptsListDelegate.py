from PySide2.QtCore import Qt
from PySide2.QtWidgets import QStyledItemDelegate, QStyle

from scripts_manager_tool.ScriptsManagerUI.modelView import ScriptRole

reload(ScriptRole)


class ScriptsListDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ScriptsListDelegate, self).__init__(parent)
    
    def paint(self, painter, option, index):
        painter.save()
        rect = option.rect
        
        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())
        
        if option.state & QStyle.State_MouseOver:
            painter.fillRect(rect, option.palette.highlight())
        
        name = index.data(ScriptRole.ScriptRole.scriptNameRole)
        
        path = index.data(ScriptRole.ScriptRole.scriptPathRole)
        script_type = index.data(ScriptRole.ScriptRole.scriptTypeRole)
        python_type = index.data(ScriptRole.ScriptRole.scriptPythonTypeRole)
        tag = index.data(ScriptRole.ScriptRole.scriptTagRole)
        
        painter.drawText(rect, Qt.AlignLeft, name)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        return super(ScriptsListDelegate, self).sizeHint(option, index)
