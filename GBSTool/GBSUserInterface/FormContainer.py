from PyQt5 import QtWidgets, QtGui

class FormContainer(QtWidgets.QWidget):
    #if the screen is big enough show input and results
    #if its not very big show input and results on seperate tabs
    def __init__(self, widgetList):
        super().__init__()
        self.widgetList = widgetList
        self.initUI()

    def initUI(self):
        #app = QtGui.QGuiApplication([])
        #screen_resolution = app.primaryScreen().geometry()
        #width, height = screen_resolution.width(), screen_resolution.height()
        width = 1005
        layout = QtWidgets.QHBoxLayout(self)
        if width > 1000:
            #side by side forms

            for l in self.widgetList:
                layout.addWidget(l)
        else:
            for l in self.widgetList:
                layout.addTab(l)
        self.setLayout(layout)