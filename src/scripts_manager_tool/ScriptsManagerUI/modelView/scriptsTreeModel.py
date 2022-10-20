# coding=utf-8
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt


class ScriptRole:
    scriptNameRole = Qt.UserRole
    scriptPathRole = Qt.UserRole + 1
    scriptTypeRole = Qt.UserRole + 2
    scriptPythonTypeRole = Qt.UserRole + 3


class TreeItem:
    def __init__(self, parent=None):
        self._parent = parent
        self._children = list()
        
        self._ptr = None
        self._level = None
        
        self._row = -1
    
    def appendChild(self, item):
        item.setRow(len(self._children))
        self._children.append(item)
    
    def removeChildren(self):
        self._children = []
    
    def child(self, row):
        return self._children[row]
    
    def parent(self):
        return self._parent
    
    def childCount(self):
        return len(self._children)
    
    def row(self):
        return self._row
    
    def setRow(self, row):
        self._row = row
    
    def setPtr(self, ptr):
        """
        存储数据的指针
        @param ptr:
        @return:
        """
        self._ptr = ptr
    
    def ptr(self):
        return self._ptr
    
    def setLevel(self, level):
        self._level = level


class ScriptsTreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(ScriptsTreeModel, self).__init__(parent)
        self._root_item = TreeItem()
    
    def root(self):
        return self._root_item
    
    def index(self, row, column, parent):
        # 在parent节点下，第row行，第column列位置上创建索引
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        parent_item = self.itemFromIndex(parent)
        item = parent_item.child(row)
        if item:
            return self.createIndex(row, column, item)
        else:
            return QModelIndex()
    
    def parent(self, index):
        # 创建index的父索引
        if not index.isValid():
            return QModelIndex()
        
        item = self.itemFromIndex(index)
        parent_item = item.parent()
        if parent_item == self._root_item:
            return QModelIndex()
        
        return self.createIndex(parent_item.row(), 0, parent_item)
    
    def data(self, index, role):
        # 获取index.row行，index.colum
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        if role == Qt.DisplayRole or role == ScriptRole.scriptNameRole:
            return item.ptr().name
    
    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        
        item = self.itemFromIndex(parent)
        return item.childCount()
    
    def columnCount(self, parent):
        return 1
    
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def insertRow(self, row, count, parent):
        pass
    
    def clear(self):
        pass
    
    def rootItem(self):
        return self._root_item
    
    def itemFromIndex(self, index):
        if index.isValid():
            item = index.internalPointer()
            return item
        
        return self._root_item
