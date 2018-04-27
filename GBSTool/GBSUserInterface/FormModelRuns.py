#Form for display model run parameters
from PyQt5 import QtWidgets, QtCore
from makeButtonBlock import makeButtonBlock
from tableHandler import tableHandler
from ModelSetTable import SetTableModel, SetTableView
from ModelRunTable import RunTableModel, RunTableView
from UIToHandler import UIToHandler
class FormModelRun(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setObjectName("modelRun")
        self.currentset = 'set1'
        self.tabs = SetsPage(self)
        self.setsTable = self.tabs
        self.runTable = self.createRunTable()

        self.layout = QtWidgets.QVBoxLayout()
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Set')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)
        self.layout.addWidget(newTabButton)
        self.layout.addWidget(self.setsTable)
        self.layout.addWidget(self.runTable)
        #self.layout.addWidget(self.runTable)
        self.setLayout(self.layout)
        self.showMaximized()


    #the run table shows ??
    def createRunTable(self):
        gb = QtWidgets.QGroupBox('Runs')

        tableGroup = QtWidgets.QVBoxLayout()

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

    def newTab(self):
        # get the set count
        tab_count = self.tabs.count()
        widg = SetsTable(self, 'Set' + str(tab_count))
        self.tabs.addTab(widg, 'Set' + str(tab_count))

        # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

class SetsPage(QtWidgets.QTabWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        set = 'Set0'
        widg = SetsTable(self, set)
        self.addTab(widg, set)




#the set table shows components to include in the set
class SetsTable(QtWidgets.QGroupBox):
    def __init__(self, parent, set):
        super().__init__(parent)
        self.init(set)

    def init(self, set):

        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons('sets'))

        tv = SetTableView(self)
        tv.setObjectName('sets')
        m = SetTableModel(self)
        m.setFilter("set_name = " + set.lower())
        tv.setModel(m)
        for r in range(m.rowCount()):
            item = m.index(r,1)
            item.flags(~QtCore.Qt.ItemIsEditable)
            m.setItemData(QtCore.QModelIndex(r,1),item)
        #hide the id column
        tv.hideColumn(0)

        tableGroup.addWidget(tv, 1)
        self.setLayout(tableGroup)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    # string -> QGroupbox
    def dataButtons(self, table):
        handler = tableHandler(self)
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()

        # buttonRow.addWidget(self.makeBlockButton(self.functionForLoadDescriptor,
        #                                          None, 'SP_DialogOpenButton',
        #                                          'Load a previously created model.'))

        buttonRow.addWidget(makeButtonBlock(self, lambda: handler.functionForNewRecord(table),
                                            '+', None,
                                            'Add'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: handler.functionForDeleteRecord(table),
                                            None, 'SP_TrashIcon',
                                            'Delete'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: UIToHandler.runModels(self),
                                            'Run', None,
                                            'Run'))
        buttonRow.addStretch(3)
        buttonBox.setLayout(buttonRow)
        return buttonBox

