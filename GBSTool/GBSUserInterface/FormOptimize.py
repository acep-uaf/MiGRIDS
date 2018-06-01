from PyQt5 import QtWidgets, QtCore
from bs4 import BeautifulSoup
import os
from GBSUserInterface.gridFromXML import gridFromXML
from GBSUserInterface.makeButtonBlock import makeButtonBlock

class FormOptimize(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.init()

    def init(self):
        self.setObjectName("modelDialog")
        widget = QtWidgets.QWidget()
        #main layout is vertical
        vlayout = QtWidgets.QVBoxLayout(self)
        #button block
        buttonBlock = QtWidgets.QGroupBox('Start Optimization',self)
        buttonBlock.setLayout(self.fillButtonBlock())
        vlayout.addWidget(buttonBlock)
        # read the config xml
        xmlFile = os.path.join(os.path.dirname(__file__), '../GBSOptimizer/Resources/optimizerConfig.xml' )
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')

        myLayout = gridFromXML(soup)
        widget.setLayout(myLayout)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        scrollArea.setWidget(widget)
        vlayout.addWidget(scrollArea)
        self.setLayout(vlayout)
        self.showMaximized()
        return

    def fillButtonBlock(self):
        buttonLayout = QtWidgets.QHBoxLayout(self)

        runButton = makeButtonBlock(self, None, text='START', icon=None, hint='Start optimization process')
        stopButton = makeButtonBlock(self, None, text='STOP', icon=None, hint='Stop optimization process')
        buttonLayout.addWidget(runButton)
        buttonLayout.addWidget(stopButton)
        return buttonLayout

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        #TODO implement an action
        #buttonFunction()
        return