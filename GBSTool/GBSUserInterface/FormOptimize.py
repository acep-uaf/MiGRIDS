from PyQt5 import QtWidgets, QtCore
from bs4 import BeautifulSoup
import os
from GBSUserInterface.gridFromXML import gridFromXML
from GBSUserInterface.makeButtonBlock import makeButtonBlock
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

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

        myLayout = gridFromXML(self,soup)
        widget.setLayout(myLayout)
        widget.setObjectName('inputGrid')
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        scrollArea.setWidget(widget)
        vlayout.addWidget(scrollArea)
        self.setLayout(vlayout)
        self.showMaximized()
        return

    def fillButtonBlock(self):
        buttonLayout = QtWidgets.QHBoxLayout()

        runButton = makeButtonBlock(self, self.startOptimize, text='START', icon=None, hint='Start optimization process')
        stopButton = makeButtonBlock(self, None, text='STOP', icon=None, hint='Stop optimization process')
        buttonLayout.addWidget(runButton)
        buttonLayout.addWidget(stopButton)
        return buttonLayout

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):

        buttonFunction()
        return
    #start running the optimize routine
    def startOptimize(self):
        #make sure values are up to date
        self.updateValues()
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,'Not implemented','If I knew how to optimize I would do it now.')
        msg.show()
        return
    #stop running the optimize routine
    def stopOptimize(self):
        return
    #if we leave the optimize form the parameters that we changed are updated
    def leaveEvent(self, event):
        self.updateValues()
        return
    def updateValues(self):
        #find the data input grid
        myGrid = self.findChild(QtWidgets.QWidget,'inputGrid')
        #get a soup of values that have changed
        newSoup, changes = update(myGrid)

        #TODO something with new soup and changes
        #should this be written to an xml file for optimizer input?
        #write changes to the database
        dbHandler = ProjectSQLiteHandler()
        for k in changes.keys():
            #if we return false upldate the existing parameter
            if not dbHandler.insertRecord(self, 'optimize_input', ['parameter','parameter_value'], [k,changes[k]]):
                dbHandler.updateRecord(self, 'optimize_input',['parameter'],[k],['parameter_value'],[changes[k]])
        return

# updates the soup to reflect changes in the form
# None->None
def update(grid):

    #soup belongs to the layout object
    layout = grid.findChild(QtWidgets.QHBoxLayout)
    soup = layout.soup
    changes = layout.changes
    # for every tag in the soup fillSetInfo its value from the form
    for tag in soup.find_all():
        if tag.parent.name not in ['component', 'childOf', 'type', '[document]']:
            parent = tag.parent.name
            pt = '.'.join([parent, tag.name])
        else:
            pt = tag.name
        for a in tag.attrs:

            widget = grid.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox, QtWidgets.QCheckBox),
                                        '.'.join([pt, str(a)]))

            if type(widget) == QtWidgets.QLineEdit:
                if tag.attrs[a] != widget.text():
                    changes['.'.join([pt, str(a)])] = widget.text()
                    tag.attrs[a] = widget.text()

            elif type(widget) == QtWidgets.QComboBox:
                if tag.attrs[a] != widget.currentText():
                    changes['.'.join([pt, str(a)])] = widget.currentText()
                    tag.attrs[a] = widget.currentText()

            elif type(widget) == QtWidgets.QCheckBox:

                if (widget.isChecked()) & (tag.attrs[a] != 'TRUE'):
                    changes['.'.join([pt, str(a)])] = 'TRUE'
                    tag.attrs[a] = 'TRUE'
                elif (not widget.isChecked()) & (tag.attrs[a] != 'FALSE'):
                    changes['.'.join([pt, str(a)])] = 'TRUE'
                    tag.attrs[a] = 'FALSE'

    return soup, changes