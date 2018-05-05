from PyQt5 import QtWidgets, QtCore

class FormContainer(QtWidgets.QWidget):
    #if the screen is big enough show input and results
    #if its not very big show input and results on seperate tabs
    def __init__(self, parent, widgetList):
        super().__init__(parent)
        self.widgetList = widgetList
        self.initUI()

    def initUI(self):
        #the current app
        app = QtCore.QCoreApplication.instance()
        #screen resolution
        screen_resolution = app.primaryScreen().geometry()

        width, height = screen_resolution.width(), screen_resolution.height()
        #layout changes dependent on width

        layout = QtWidgets.QHBoxLayout(self)
        if width > 1000:
            #side by side forms for wide screens

            for l in self.widgetList:
                layout.addWidget(l)
        else:
            #tabs for small screens
            tabArea = QtWidgets.QTabWidget(self)
            for l in self.widgetList:
                tabArea.addTab(l, l.objectName())
            layout.addWidget(tabArea)
        self.setLayout(layout)