from PyQt5 import QtWidgets
from GBSUserInterface.FileBlock import FileBlock

#each page contains information for a single file
#calls the specific page type during initiation

class Pages(QtWidgets.QTabWidget):
    #QtWidget,String, Class ->
    def __init__(self, parent,name,pageclass):
        super().__init__(parent)
        self.name = name
        self.init(pageclass)

    def init(self,pageclass):
        widg = pageclass(self, self.name)
        self.addTab(widg, self.name)

