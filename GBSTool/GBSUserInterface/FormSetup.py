
from PyQt5 import QtCore, QtWidgets
import ModelComponentTable as T
import ModelEnvironmentTable as E
from gridLayoutSetup import setupGrid
from SetupWizard import SetupWizard
from WizardTree import WizardTree
from ModelSetupInformation import ModelSetupInformation
from GBSInputHandler.Component import Component
from UIToHandler import UIToHandler
from makeButtonBlock import makeButtonBlock
from ResultsSetup import  ResultsSetup
from FormModelRuns import SetsTableBlock
from ProjectSQLiteHandler import ProjectSQLiteHandler


class FormSetup(QtWidgets.QWidget):
    global model
    model = ModelSetupInformation()
    def __init__(self, parent):
        super().__init__(parent)
        
        self.initUI()
    #initialize the form
    def initUI(self):

        self.setObjectName("setupDialog")

        self.model = model

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()
        self.createButtonBlock()
        #the top block is buttons to load setup xml and data files

        windowLayout.addWidget(self.ButtonBlock,2)
        #create some space between the buttons and xml setup block


        #add the setup block
        self.createTopBlock()
        #the topBlock is hidden until we load or create a setup xml
        self.topBlock.setEnabled(False)
        windowLayout.addWidget(self.topBlock)
        #more space between component block

        #TODO move to seperate file
        dlist = [
            [{'title': 'Time Series Data', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'inputFileDirvalue', 'folder': True}, 'Data Input Format'],

            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'hydroFileDirvalue', 'folder': True}, 'Data Input Format'],

            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'windFileDirvalue', 'folder': True}, 'Data Input Format'],

            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_data_format', 'name': 'inputFileFormatvalue', 'folder': False},
             'Project'],

            [{'title': 'Project', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'project', 'folder': False}, None, ]

        ]

        self.WizardTree = self.buildWizardTree(dlist)
        self.createTableBlock('Components', 'components', self.assignComponentBlock)
        self.componentBlock.setEnabled(False)
        windowLayout.addWidget(self.componentBlock)

        # the bottom block is disabled until a setup file is created or loaded
        self.createTableBlock('Environment Data', 'environment', self.assignEnvironmentBlock)
        self.environmentBlock.setEnabled(False)
        windowLayout.addWidget(self.environmentBlock)


        windowLayout.addWidget(makeButtonBlock(self,self.createInputFiles,'Create input files',None,'Create input files to run models'),3)

        #set the main layout as the layout for the window

        self.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Setup')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #show the form
        self.showMaximized()

    # Setters
    #(String, number, list or Object) ->
    def assignEnvironmentBlock(self, value):
        self.environmentBlock = value

    def assignComponentBlock(self,value):
        self.componentBlock = value

    #FormSetup -> QWidgets.QHBoxLayout
    #creates a horizontal button layout to insert in FormSetup
    def createButtonBlock(self):
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        #layout object name
        hlayout.setObjectName('buttonLayout')
        #add the button to load a setup xml

        hlayout.addWidget(makeButtonBlock(self, self.functionForLoadButton,
                                 'Load Existing Project', None, 'Load a previously created project files.'))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            makeButtonBlock(self,self.functionForCreateButton,
                                 'Create setup XML', None, 'Start the setup wizard to create a new setup file'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)
        hlayout.addStretch(1)
        self.ButtonBlock.setLayout(hlayout)

        self.ButtonBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        #self.ButtonBlock.setMinimumSize(self.size().width(),self.minimumSize().height())
        return hlayout

    #method -> None
    #calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self,buttonFunction):
        buttonFunction()

    #FormSetup -> None
    #method to modify FormSetup content
    def functionForCreateButton(self):

        #make a database
        #s is the 1st dialog box for the setup wizard

        s = SetupWizard(self.WizardTree, model, self)


        #display collected data
        hasSetup = model.feedSetupInfo()

        self.projectDatabase = False
        if hasSetup:
            self.fillData(model)
            self.topBlock.setEnabled(True)
            self.environmentBlock.setEnabled(True)
            self.componentBlock.setEnabled(True)
            #enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget,'pages')
            pages.enableTabs()

    #searches for and loads existing project data - database, setupxml,descriptors, data object
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''
        import os
        from replaceDefaultDatabase import replaceDefaultDatabase

        if (self.model.project == '') | (self.model.project is None):
            #launch file navigator to identify setup file
            setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", None, "*xml" )
            if (setupFile == ('','')) | (setupFile is None):
                return
            model.assignSetupFolder(setupFile[0])


            #Look for an existing component database and replace the default one with it
            if os.path.exists(os.path.join(self.model.projectFolder,'project_manager')):
                print('An existing project database was found for %s.' %self.model.project)

                replaceDefaultDatabase(os.path.join(self.model.projectFolder, 'project_manager'))
                self.projectDatabase = True
            else:
                self.projectDatabase = False
                print('An existing project database was not found for %s.' % self.model.project)

            # assign setup information to data model
            model.feedSetupInfo()

            # display data
            self.fillData(model)

            # look for an existing data pickle
            handler = UIToHandler()
            self.model.data = handler.loadInputData(os.path.join(self.model.setupFolder, self.model.project + 'Setup.xml'))
            if self.model.data is not None:
                self.updateModelPage(self.model.data)

                #refresh the plot
                resultDisplay = self.parent().findChild(ResultsSetup)
                resultDisplay.defaultPlot(self.model.data)

            #make the data blocks editable
            self.topBlock.setEnabled(True)
            self.environmentBlock.setEnabled(True)
            self.componentBlock.setEnabled(True)
            # enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget, 'pages')
            pages.enableTabs()
            print('Loaded %s:' % model.project)
        else:
            #TODO allow new projects to be loaded with out closing window
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Close project", "You need to close the sofware before you load a new project")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

    #TODO make dynamic from list input
    def buildWizardTree(self, dlist):

        w1 = WizardTree(dlist[0][0], dlist[0][1], 2, [])
        #w2 = WizardTree(dlist[1][0], dlist[1][1], 1, [])  # hydro
        w3 = WizardTree(dlist[2][0], dlist[2][1], 0, [])  # wind
        w4 = WizardTree(dlist[3][0], dlist[3][1], 0, [w1, w3])  # inputFileFormat
        w5 = WizardTree(dlist[4][0], dlist[4][1], 0, [w4])
        return w5

    #FormSetup -> FormSetup
    #creates a horizontal layout containing gridlayouts for data input
    def createTopBlock(self):
         #create a horizontal grouping to contain the top setup xml portion of the form
        self.topBlock = QtWidgets.QGroupBox('Setup XML')
        hlayout = QtWidgets.QHBoxLayout()
        
        hlayout.setObjectName("layout1")
        
        #add the setup grids
        g1 = {'headers':['Attribute','Field','Format'],
                          'rowNames':['Date','Time','Load'],
                          'columnWidths': [1, 1, 1],
                          'Date':{'Field':{'widget':'txt','name':'dateChannelvalue'},
                                  'Format':{'widget':'combo','items':['ordinal'],'name':'dateChannelformat'},
                                            },
                          'Time':{'Field':{'widget':'txt','name':'timeChannelvalue'},
                                 'Format':{'widget':'combo','items':['excel'],'name':'timeChannelformat'}
                                  },
                          'Load':{'Field':{'widget':'txt','name':'realLoadChannelvalue'},
                                 'Format':{'widget':'combo','items':['KW','W','MW'],'name':'realLoadChannelunit'}}}
        grid = setupGrid(g1)
        hlayout.addLayout(grid)
        hlayout.addStretch(1)    
        #add the second grid
        g2 = {'headers':['TimeStep','Value','Units'],
                          'rowNames':['Input','Output'],
                          'columnWidths': [1, 1, 1],
                          'Input':{'Value':{'widget':'txt','name':'inputTimeStepvalue'},
                                    'Units':{'widget':'combo','items':['S','M','H'],'name':'inputTimeStepunit'}
                                   },
                          'Output':{'Value':{'widget':'txt','name':'outputTimeStepvalue'},
                                    'Units':{'widget':'combo','items':['S','M','H'],'name':'outputTimeStepunit'}}
                          }
        grid = setupGrid(g2)
        hlayout.addLayout(grid)

        #add another stretch to keep the grids away from the right edge
        hlayout.addStretch(1)
        self.topBlock.setObjectName('format')
        self.topBlock.setLayout(hlayout)
        self.topBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.topBlock.sizePolicy().retainSizeWhenHidden()

    #layout for tables
    def createTableBlock(self, title, table, fn):

        gb = QtWidgets.QGroupBox(title)

        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons(table))
        if table =='components':
            tv = T.ComponentTableView(self)
            tv.setObjectName('components')
            m = T.ComponentTableModel(self)

        else:
            tv = E.EnvironmentTableView(self)
            tv.setObjectName('environment')
            m = E.EnvironmentTableModel(self)
        tv.setModel(m)

        tv.hideColumn(0)

        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        fn(gb)
        return

    #Load an existing descriptor file and populate the component table
    #-> None
    def functionForLoadDescriptor(self):
        #TODO temporary message to prevent unique index error
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Load Descriptor',
                                    'If the component descriptor file you are loading has the same name as an existing component it will not load')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

        tableView = self.findChild((QtWidgets.QTableView), 'components')
        model = tableView.model()
        #identify the xml
        descriptorFile = QtWidgets.QFileDialog.getOpenFileName(self, "Select a descriptor file", None, "*xml")
        if (descriptorFile == ('', '')) | (descriptorFile is None):
            return

        fieldName, ok = QtWidgets.QInputDialog.getText(self, 'Field Name','Enter the name of the channel that contains data for this component.')
        #if a field was entered add it to the table model and database
        if ok:
            record = model.record()
            record.setValue('original_field_name',fieldName)

            handler = UIToHandler()
            record = handler.copyDescriptor(descriptorFile[0],self.model.componentFolder, record)

            #add a row into the database
            model.insertRowIntoTable(record)
            # refresh the table
            model.select()
        return

    # Add an empty record to the specified datatable
    # String -> None
    def functionForNewRecord(self, table):
        #add an empty record to the table

        #get the model
        tableView= self.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        #insert an empty row as the last record

        model.insertRows(model.rowCount(),1)
        #TODO persistent editors and delegats need to be set
        model.submitAll()

    #delete the selected record from the specified datatable
    #String -> None
    def functionForDeleteRecord(self, table):

        #get selected rows
        tableView = self.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        #selected is the indices of the selected rows
        selected = tableView.selectionModel().selection().indexes()
        if len(selected) == 0:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,'Select Rows','Select rows before attempting to delete')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,'Confirm Delete','Are you sure you want to delete the selected records?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)

            result = msg.exec()

            if result == 1024:
                handler = UIToHandler()
                removedRows = []
                for r in selected:
                    if r.row() not in removedRows:
                        if table == 'components':
                            # remove the xml files too
                            handler.removeDescriptor(model.data(model.index(r.row(), 3)), self.model.componentFolder)
                        removedRows.append(r.row())
                        model.removeRows(r.row(),1)



                #Delete the record from the database and refresh the tableview
                model.submitAll()
                model.select()

    #string -> QGroupbox
    def dataButtons(self,table):
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()

        if table == 'components':

            buttonRow.addWidget(makeButtonBlock(self,self.functionForLoadDescriptor,
                                               None, 'SP_DialogOpenButton', 'Load a previously created component xml file.'))

        buttonRow.addWidget(makeButtonBlock(self,lambda:self.functionForNewRecord(table),
                                             '+', None,
                                             'Add a component'))
        buttonRow.addWidget(makeButtonBlock(self,lambda:self.functionForDeleteRecord(table),
                                             None, 'SP_TrashIcon',
                                             'Delete a component'))
        buttonRow.addStretch(3)
        buttonBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        buttonBox.setLayout(buttonRow)
        return buttonBox

    #inserts data from the data model into corresponding boxes on the screen
    #SetupInfo -> None
    def fillData(self,model):

        from ProjectSQLiteHandler import ProjectSQLiteHandler

        d = model.getSetupTags()

        #for every key in d find the corresponding textbox or combo box

        for k in d.keys():

            for a in d[k]:
                if d[k][a] is not None:
                    edit_field = self.findChild((QtWidgets.QLineEdit,QtWidgets.QComboBox), k + a)

                    if type(edit_field) is QtWidgets.QLineEdit:

                        edit_field.setText(d[k][a])
                    elif type(edit_field) is QtWidgets.QComboBox:
                        edit_field.setCurrentIndex(edit_field.findText(d[k][a]))


        def getDefault(l,i):
            try:
                l[i]
                return l[i]
            except IndexError:
                return 'NA'
        #this is what happens if there isn't already a project database.
        if not self.projectDatabase:

            # for headers, componentnames, componentattributes data goes into the database for table models
            dbHandler = ProjectSQLiteHandler('project_manager')
            for i in range(len(model.headerName.value)):


                fields = ('original_field_name','component_name','attribute','units')
                if (getDefault(model.headerName.value,i) != 'None'):
                    values = (getDefault(model.headerName.value,i), getDefault(model.componentName.value,i),
                          getDefault(model.componentAttribute.value,i), getDefault(model.componentAttribute.unit,i))


                    if getDefault(model.componentAttribute.value,i) in ['WS','WF','IR','Tamb','Tstorage']:
                        #insert into environment table
                        table = 'environment'
                    else:
                         table = 'components'

                    if len(dbHandler.cursor.execute("select * from " + table + " WHERE component_name = '" + getDefault(model.componentName.value,i) + "'").fetchall()) < 1:
                         dbHandler.insertRecord(table,fields,values)
            dbHandler.closeDatabase()

        #refresh the tables
        tableView = self.findChild((QtWidgets.QTableView), 'environment')
        tableModel= tableView.model()
        tableModel.select()
        tableView = self.findChild((QtWidgets.QTableView), 'components')
        tableModel = tableView.model()
        tableModel.select()
        return

    #send input data to the ModelSetupInformation data model
    def sendSetupData(self):
        #cycle through the input children in the topblock
        for child in self.topBlock.findChildren((QtWidgets.QLineEdit,QtWidgets.QComboBox)):

            if type(child) is QtWidgets.QLineEdit:
                value = child.text()

            else:
                value = child.itemText(child.currentIndex())

            self.model.assign(child.objectName(),value)
        #we also need headerNames, componentNames, attributes and units from the component section
        componentView = self.findChild((QtWidgets.QTableView),'components')
        componentModel = componentView.model()
        headerName=[]
        componentName = []
        componentAttribute = []
        componentAttributeU = []
        #list of distinct components
        self.components=[]
        for i in range(0,componentModel.rowCount()):

            headerName.append(componentModel.data(componentModel.index(i,1)))
            componentName.append(componentModel.data(componentModel.index(i,3)))
            componentAttribute.append(componentModel.data(componentModel.index(i,7)))
            componentAttributeU.append(componentModel.data(componentModel.index(i,4)))
            c = Component(component_Name =componentModel.data(componentModel.index(i,3)),
                          scale=componentModel.data(componentModel.index(i,5)),
                          units=componentModel.data(componentModel.index(i,4)),
                        offset = componentModel.data(componentModel.index(i,6)),
                          attribute=componentModel.data(componentModel.index(i,7)),
                          type = componentModel.data(componentModel.index(i,2)))
            self.components.append(c)
        #make a list of distinct values
        componentNames = list(set(componentName))
        #and the same data from the environment section
        envView = self.findChild((QtWidgets.QTableView), 'environment')
        envModel = envView.model()
        for j in range(0, envModel.rowCount()):
            headerName.append(envModel.data(envModel.index(j, 1)))
            componentName.append(envModel.data(envModel.index(j, 2)))
            componentAttribute.append(envModel.data(envModel.index(j, 6)))
            componentAttributeU.append(envModel.data(envModel.index(j, 3)))
        model.assign('headerNamevalue',headerName)
        model.assign('componentNamevalue', componentName)
        model.assign('componentAttributevalue', componentAttribute)
        model.assign('componentAttributeunit', componentAttributeU)
        model.assign('componentNamesvalue', componentNames)

    #write data to the data model and generate input xml files for setup and components
    def createInputFiles(self):
        import os
        from ProjectSQLiteHandler import ProjectSQLiteHandler
        self.sendSetupData()
        # write all the xml files

        # start with the setupxml
        self.model.writeNewXML()

        #make sure the necessary information is filled in
        #required: input folder, data format, date-time fields, component max power
        # import datafiles
        handler = UIToHandler()
        cleaned_data, componentDict = handler.loadFixData(os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.updateModelPage(cleaned_data)
        # generate netcdf files
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Time Series loaded",
                                    "Do you want to generate netcdf files?.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        result = msg.exec()
        #if yes create the input netcdf files otherwise pickle the dataframe for later use
        if result == 1024:
            handler.createNetCDF(cleaned_data, componentDict, None, os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        else:
            #pickle the data to be used later
            handler.storeData(cleaned_data,os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        return
    #DataObject with data frame called 'fixed' and field 'datetime'
    def updateModelPage(self, data):
        # start and end dates get set written to database as default date ranges
        import pandas as pd
        defaultStart = str((pd.to_datetime(data.fixed.index, unit='s')[0]).date())
        defaultEnd = str((pd.to_datetime(data.fixed.index, unit='s')[len(data.fixed.index) -1]).date())

        sqlHandler = ProjectSQLiteHandler()
        sqlHandler.cursor.execute("UPDATE setup set date_start = ?, date_end = ? where set_name = 'default'",
                                  [defaultStart, defaultEnd])
        sqlHandler.connection.commit()
        sqlHandler.closeDatabase()
        # tell the model form to update now that there is data
        modelForm = self.window().findChild(SetsTableBlock)
        # start and end are tuples at this point
        modelForm.update(start=defaultStart, end=defaultEnd, components=','.join(self.model.componentNames.value))

    #event triggered when user navigates away from setup page
    def leaveEvent(self, event):
        # move the default database to the project folder and save xmls
        if 'projectFolder' in self.model.__dict__.keys():
            # on close save the xml files
            self.sendSetupData()
            self.model.writeNewXML()
    # close event is triggered when the form is closed
    def closeEvent(self, event):
        #move the default database to the project folder and save xmls
        if 'projectFolder' in self.model.__dict__.keys():
            # on close save the xml files
            self.sendSetupData()
            self.model.writeNewXML()
