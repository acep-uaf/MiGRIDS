#Form for display model run parameters
from PyQt5 import QtWidgets, QtCore, QtGui
from makeButtonBlock import makeButtonBlock
from TableHandler import TableHandler
from ModelSetTable import SetTableModel, SetTableView
from ModelRunTable import RunTableModel, RunTableView
from ProjectSQLiteHandler import ProjectSQLiteHandler
from UIToHandler import UIToHandler
import datetime

class FormModelRun(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setObjectName("modelRun")

        self.tabs = SetsPage(self, 'set0')
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
        widg = SetsTable(self, 'set' + str(tab_count))
        self.tabs.addTab(widg, 'Set' + str(tab_count))

        # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

class SetsPage(QtWidgets.QTabWidget):

    def __init__(self, parent,set):
        super().__init__(parent)
        self.set = set
        self.initUI()

    def initUI(self):

        widg = SetsTable(self, self.set)
        self.addTab(widg, self.set)




#the set table shows components to include in the set
class SetsTable(QtWidgets.QGroupBox):
    def __init__(self, parent, set):
        super().__init__(parent)
        self.init(set)

    def init(self, set):

        self.set = set
        handler = ProjectSQLiteHandler('project_manager')
        defaultDate = handler.cursor.execute("select date_start from setup where set_name = 'default'").fetchone()
        defaultDate = datetime.datetime.strptime(defaultDate[0], '%m/%d/%Y')
        self.startDate = defaultDate

        defaultDate = handler.cursor.execute("select date_end from setup where set_name = 'default'").fetchone()
        defaultDate = datetime.datetime.strptime(defaultDate[0], '%m/%d/%Y')
        self.endDate = defaultDate
        handler.closeDatabase()
        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons('sets'))


        tv = SetTableView(self,column1=self.set)
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
    def setInfo(self):
        infoBox = QtWidgets.QGroupBox()
        infoRow = QtWidgets.QHBoxLayout()
        # time range filters
        infoRow.addWidget(QtWidgets.QLabel('Filter Date Range: '))
        infoRow.addWidget(self.dateSelector(True))
        infoRow.addWidget(QtWidgets.QLabel(' to '))
        infoRow.addWidget(self.dateSelector(False))

        infoRow.addWidget(QtWidgets.QLabel('Timestep:'))
        timestepWidget = QtWidgets.QLineEdit('1')

        timestepWidget.setValidator(QtGui.QIntValidator())
        infoRow.addWidget(timestepWidget,1)

        infoRow.addWidget(QtWidgets.QLabel('Seconds'),2)
        infoRow.addStretch(1)
        infoRow.addWidget(QtWidgets.QLabel('Components'))
        infoRow.addWidget(self.componentSelector())
        infoBox.setLayout(infoRow)

        return infoBox
    #->QtWidgets.QLineEdit
    def componentSelector(self):
        from Delegates import ClickableLineEdit

        self.componentDefault = None


        widg = ClickableLineEdit(self.componentDefault)
        widg.setObjectName('components')

        widg.clicked.connect(lambda: self.componentCellClicked())
        return widg

    @QtCore.pyqtSlot()
    def componentCellClicked(self):
        from DialogComponentList import ComponentSetListForm
        from ProjectSQLiteHandler import ProjectSQLiteHandler
        from Delegates import ComboDelegate, ComponentFormOpenerDelegate
        import pandas as pd
        handler = ProjectSQLiteHandler('project_manager')

        # get the cell, and open a listbox of possible components for this project
        checked = pd.read_sql_query("select component_name from components", handler.connection)

        checked = list(checked['component_name'])
        handler.closeDatabase()
        # checked is a comma seperated string but we need a list
        #checked = checked.split(',')
        listDialog = ComponentSetListForm(checked)
        components = listDialog.checkedItems()
        # format the list to be inserted into a text field in a datatable
        str1 = ','.join(components)
        widg = self.findChild(QtWidgets.QLineEdit,'components')
        widg.setText(str1)

        #find the component drop down delegate and reset its list to components
        tv = self.findChild(QtWidgets.QWidget,'sets')
        #assumes the only ComboDelegate is the component selector
        cb = tv.findChild(ComboDelegate)
        lm = cb.values
        lm.setStringList(components)



    #Boolean -> #QtWidget.QDateEdit()
    def dateSelector(self,start = True):

        widg = QtWidgets.QDateEdit()
        #default is entire dataset

        if start:
           widg.setDate(QtCore.QDate(self.startDate.year,self.startDate.month,self.startDate.day))

        else:
            widg.setDate(QtCore.QDate(self.endDate.year, self.endDate.month, self.endDate.day))

        widg.setDateRange(self.startDate, self.endDate)
        return widg

    # string -> QGroupbox
    def dataButtons(self, table):
        handler = TableHandler(self)
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
        buttonRow.addWidget(self.setInfo())
        buttonBox.setLayout(buttonRow)
        return buttonBox

