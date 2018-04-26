from PyQt5 import QtWidgets


class ResultsModel(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.init()

    def init(self):
        self.showMaximized()
        return