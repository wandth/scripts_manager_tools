from PySide2.QtCore import QTimer, Signal, QObject

class DelayedExecutionTimer(QObject):
    triggered = Signal(str)

    def __init__(self, maxDelay=2000, minDelay=500, parent=None):
        super(DelayedExecutionTimer, self).__init__(parent)
        # The min delay is the time the class will wait after being triggered before emitting the triggered() signal
        # (if there is no key press for this time: trigger)
        self.minDelay = minDelay
        self.maxDelay = maxDelay
        self.minTimer = QTimer(self)
        self.maxTimer = QTimer(self)
        self.minTimer.timeout.connect(self.timeout)
        self.maxTimer.timeout.connect(self.timeout)

    def timeout(self):
        self.minTimer.stop()
        self.maxTimer.stop()
        self.triggered.emit(self.string)

    def trigger(self, string):
        self.string = string
        if not self.maxTimer.isActive():
            self.maxTimer.start(self.maxDelay)
        self.minTimer.stop()
        self.minTimer.start(self.minDelay)
