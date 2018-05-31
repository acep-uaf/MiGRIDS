from PyQt5 import QtWidgets
from bs4 import BeautifulSoup
import os
from GBSUserInterface.gridFromXML import gridFromXML
class FormOptimize(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.init()

    def init(self):
        self.setObjectName("modelDialog")
        # read the config xml
        xmlFile = os.path.join(os.path.dirname(__file__), '../GBSOptimizer/Resources/optimizerConfig.xml' )
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')

        myLayout = gridFromXML(soup)
        self.setLayout(myLayout)
        self.showMaximized()
        return