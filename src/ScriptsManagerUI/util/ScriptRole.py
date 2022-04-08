from PySide2.QtCore import Qt
from pymel.util import Enum


class ScriptRole(Enum) :
    scriptNameRole = Qt.UserRole
    scriptPathRole = Qt.UserRole + 1
    scriptTypeRole = Qt.UserRole + 2
    scriptPythonTypeRole = Qt.UserRole + 3
    scriptTagRole = Qt.UserRole + 4
