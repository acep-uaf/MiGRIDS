#Form for display model run parameters
from PyQt5 import QtWidgets, QtCore, QtGui
from GBSUserInterface.makeButtonBlock import makeButtonBlock
from GBSUserInterface.TableHandler import TableHandler
from GBSUserInterface.ModelSetTable import SetTableModel, SetTableView
from GBSUserInterface.ModelRunTable import RunTableModel, RunTableView
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from GBSController.UIToHandler import UIToHandler
from GBSUserInterface.Pages import Pages
import datetime
import os

#main form containing setup and run information for a project
class FormModelRun(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setObjectName("modelDialog")
        #the first page is for set0
        #self.tabs = SetsPages(self, 'Set0')
        self.tabs = Pages(self,'Set0',SetsTableBlock)
        self.tabs.setObjectName('modelPages')
        #self.setsTable = self.tabs
        #create the run table
        self.runTable = self.createRunTable()

        self.layout = QtWidgets.QVBoxLayout()

        #button to create a new set tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Set')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)
        self.layout.addWidget(newTabButton)
        #set table goes below the new tab button

        self.layout.addWidget(self.tabs)
        #runs are at the bottom
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

    #add a new set to the project, this adds a new tab for the new set information
    def newTab(self):
        # get the set count
        tab_count = self.tabs.count()
        widg = SetsTableBlock(self, 'set' + str(tab_count))
        widg.fillSetInfo()
        self.tabs.addTab(widg, 'Set' + str(tab_count))

        #create a folder to hold the relevent set data
        #project folder is from FormSetup model
        projectFolder = self.window().findChild(QtWidgets.QWidget, "setupDialog").model.projectFolder
        newFolder = os.path.join(projectFolder,'OutputData', 'Set' + str(tab_count))
        if not os.path.exists(newFolder):
            os.makedirs(newFolder)

    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()



#the set table shows components to include in the set and attributes to change for runs
class SetsTableBlock(QtWidgets.QGroupBox):
    def __init__(self, parent, set):
        super().__init__(parent)
        self.init(set)

    def init(self, set):

        self.componentDefault = []
        self.set = set
        #get default date ranges
        self.getDefaultDates()
        #main layouts
        tableGroup = QtWidgets.QVBoxLayout()
        #setup info for a set

        self.setInfo = self.makeSetInfo()
        tableGroup.addWidget(self.setInfo)

        #buttons for adding and deleting set records
        tableGroup.addWidget(self.dataButtons('sets'))
        #the table view filtered to the specific set for each tab
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
        if set is not None:
            self.fillSetInfo(set)
        else:
            self.fillSetInfo()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #fill form with existing data
    def fillData(self,set):
       return
    #sets the start and end date for a set.
    #if no values are provided the values are drawn from the database
    #tuple(s) -> None
    def getDefaultDates(self, **kwargs):
        #tuples
        start = kwargs.get('start')
        end = kwargs.get('end')

        handler = ProjectSQLiteHandler()
        if start == None:
            start = handler.cursor.execute("select date_start from setup where set_name = 'default'").fetchone()
        if end == None:
            end = handler.cursor.execute("select date_end from setup where set_name = 'default'").fetchone()
        handler.closeDatabase()

        #format the tuples from database output to datetime objects
        if type(start)== str:
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')
        else:
            start = datetime.datetime.strptime(start[0], '%Y-%m-%d')
            end = datetime.datetime.strptime(end[0], '%Y-%m-%d')
        self.startDate = start
        self.endDate = end
        return
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()


    #->QtWidgets.QGroupBox
    def makeSetInfo(self, **kwargs):
        set = kwargs.get("set")

        infoBox = QtWidgets.QGroupBox()
        infoRow = QtWidgets.QHBoxLayout()
        # time range filters
        infoRow.addWidget(QtWidgets.QLabel('Filter Date Range: '))
        ds = self.makeDateSelector(True)
        infoRow.addWidget(ds)
        infoRow.addWidget(QtWidgets.QLabel(' to '))
        de = self.makeDateSelector(False)
        infoRow.addWidget(de)

        infoRow.addWidget(QtWidgets.QLabel('Timestep:'))
        timestepWidget = QtWidgets.QLineEdit('1')
        timestepWidget.setObjectName(('timestep'))
        timestepWidget.setValidator(QtGui.QIntValidator())
        infoRow.addWidget(timestepWidget)

        infoRow.addWidget(QtWidgets.QLabel('Seconds'),1)

        infoRow.addWidget(QtWidgets.QLabel('Components'))
        infoRow.addWidget(self.componentSelector(),2)
        infoBox.setLayout(infoRow)

        return infoBox

    #->QtWidgets.QLineEdit
    def componentSelector(self,**kwargs):
        from GBSUserInterface.Delegates import ClickableLineEdit
        #if components are not provided use the default list
        if kwargs.get("components"):
            components = kwargs.get("components")
        else:
            components = self.componentDefault


        widg = ClickableLineEdit(','.join(components))
        widg.setObjectName('componentNames')

        widg.clicked.connect(lambda: self.componentCellClicked())
        return widg
    #fills the setup portion of a set tab with either default values or current database values
    #String -> None
    def fillSetInfo(self, set = 'default'):

        databaseHandler = ProjectSQLiteHandler()
        # dictionary of set info
        setInfo = databaseHandler.getSetInfo(set)
        databaseHandler.closeDatabase()
        if type(setInfo['component_names']) == str:
            self.componentDefault = setInfo['component_names'].split(',')
        else:
            self.componentDefault = setInfo['component_names']
        start = datetime.datetime.strptime(setInfo['min_date'],'%Y-%m-%d')
        end = datetime.datetime.strptime(setInfo['max_date'],'%Y-%m-%d')


        #dates are strings here but they need to be datetimes
        self.startDate = setInfo.get('date_start')
        self.endDate = setInfo.get('date_end')
        self.getDefaultDates(start=self.startDate, end=self.endDate)
        #fillSetInfo the widget values

        self.setDateSelectorProperties(self.findChild(QtWidgets.QDateEdit, 'startDate'))
        self.setDateSelectorProperties(self.findChild(QtWidgets.QDateEdit, 'endDate'),False)
        self.findChild(QtWidgets.QDateEdit, 'startDate').setDateRange(start, end)
        self.findChild(QtWidgets.QDateEdit, 'endDate').setDateRange(start, end)
        self.findChild(QtWidgets.QLineEdit,'componentNames').setText(','.join(self.componentDefault))
        self.updateComponentDelegate(self.componentDefault)

        return
    #update the component drop down in the set table to include the selected or default components
    def updateComponentDelegate(self,components):
        from GBSUserInterface.Delegates import ComboDelegate, ComponentFormOpenerDelegate
        # find the component drop down delegate and reset its list to the selected components
        tv = self.findChild(QtWidgets.QWidget, 'sets')

        cbs = tv.findChildren(ComboDelegate)
        for c in cbs:

            if c.name == 'componentName':
                lm = c.values
                lm.setStringList(components)

    @QtCore.pyqtSlot()
    def componentCellClicked(self):
        from GBSUserInterface.DialogComponentList import ComponentSetListForm
        from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

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
        widg = self.findChild(QtWidgets.QLineEdit,'componentNames')
        widg.setText(str1)
        self.updateComponentDelegate(components)

    #Boolean -> QDateEdit
    def makeDateSelector(self, start=True):
        widg = QtWidgets.QDateEdit()
        if start:
            widg.setObjectName('startDate')
        else:
            widg.setObjectName('endDate')
        return widg

    #QDateEdit, Boolean -> QDateEdit()
    def setDateSelectorProperties(self, widg, start = True):
        # default is entire dataset
        if start:
           widg.setDate(QtCore.QDate(self.startDate.year,self.startDate.month,self.startDate.day))

        else:
            widg.setDate(QtCore.QDate(self.endDate.year, self.endDate.month, self.endDate.day))


        widg.setDisplayFormat('yyyy-MM-dd')
        widg.setCalendarPopup(True)
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
                                            'Add a component change'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: handler.functionForDeleteRecord(table),
                                            None, 'SP_TrashIcon',
                                            'Delete a component change'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: self.runSet(),
                                            'Run', None,
                                            'Run Set'))
        buttonRow.addStretch(3)

        buttonBox.setLayout(buttonRow)
        return buttonBox

    def runSet(self):
        # currentSet
        currentSet = self.set
        #set info needs to be updated in the database
        setInfo = (
            currentSet,
            self.findChild(QtWidgets.QDateEdit,'startDate').text(),
            self.findChild(QtWidgets.QDateEdit, 'endDate').text(),
            self.findChild(QtWidgets.QLineEdit,'timestep').text(),
            self.findChild(QtWidgets.QLineEdit,'componentNames').text()
        )
        sqlhandler = ProjectSQLiteHandler()
        try:
            sqlhandler.cursor.execute("INSERT INTO setup(set_name, date_start, date_end, timestep, component_names) VALUES(?,?,?,?,?)",setInfo)
        except:
            sqlhandler.cursor.execute(
                "UPDATE setup set date_start = ?, date_end=?, timestep=?, component_names=? WHERE set_name = '" + setInfo[0] + "'", setInfo[1:])
        sqlhandler.connection.commit()
        sqlhandler.closeDatabase()
        uihandler = UIToHandler()

        # component table is the table associated with the button
        componentTable = self.findChild(SetTableView).model()
        if componentTable.rowCount() > 0:

            uihandler.runModels(currentSet, componentTable,self.window().findChild(QtWidgets.QWidget,'setupDialog').model)
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Add components",
                                        "You need to select component attributes to alter before running sets.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
