from PySide2.QtWidgets import QCheckBox


class CheckableTag(QCheckBox) :
    def __init__(self, name, parent = None) :
        super(CheckableTag, self).__init__(name, parent)
