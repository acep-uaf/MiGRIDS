#Form for display model run parameters
from PyQt5 import QtWidgets, QtCore
from makeButtonBlock import makeButtonBlock
from tableHandler import tableHandler
from ModelSetTable import SetTableModel, SetTableView
from ModelRunTable import RunTableModel, RunTableView
class ModelRunForm(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setObjectName("modelRun")
        self.currentset = 'set1'
        self.setsTable = self.createSetTable()
        self.runTable = self.createRunTable()
        #TODO look up run table name

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.setsTable)
        self.layout.addWidget(self.runTable)
        #self.layout.addWidget(self.runTable)
        self.setLayout(self.layout)
        self.showMaximized()

    #the set table shows components to include in the set
    def createSetTable(self):
        gb = QtWidgets.QGroupBox('Sets')

        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons('sets'))

        tv = SetTableView(self)
        tv.setObjectName('sets')
        m = SetTableModel(self)
        tv.setModel(m)
        #hide the id column
        tv.hideColumn(0)

        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        return gb

    #the run table shows ??
    def createRunTable(self):
        gb = QtWidgets.QGroupBox('Runs')

        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons('runs'))

        tv = RunTableView(self)
        tv.setObjectName('runs')
        m = RunTableModel(self)
        tv.setModel(m)

        # hide the id column
        tv.hideColumn(0)

        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        return gb

    # string -> QGroupbox
    def dataButtons(self, table):
        handler = tableHandler(self)
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()


        # buttonRow.addWidget(self.makeBlockButton(self.functionForLoadDescriptor,
        #                                          None, 'SP_DialogOpenButton',
        #                                          'Load a previously created model.'))

        buttonRow.addWidget(makeButtonBlock(self,lambda: handler.functionForNewRecord(table),
                                                 '+', None,
                                                 'Add'))
        buttonRow.addWidget(makeButtonBlock(self,lambda: handler.functionForDeleteRecord(table),
                                                 None, 'SP_TrashIcon',
                                                 'Delete'))
        buttonRow.addStretch(3)
        buttonBox.setLayout(buttonRow)
        return buttonBox

        # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

