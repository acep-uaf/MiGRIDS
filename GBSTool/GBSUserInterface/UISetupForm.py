
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
import ComponentTableModel as T
import EnvironmentTableModel as E
from gridLayoutSetup import setupGrid
from SetupWizard import SetupWizard
from WizardTree import WizardTree
from ConsoleDisplay import ConsoleDisplay
from SetupInformation import SetupInformation
from ComponentSQLiteHandler import SQLiteHandler
from Component import Component
from UIToHandler import UIToHandler

class SetupForm(QtWidgets.QWidget):
    global model
    model = SetupInformation()
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        self.setObjectName("setupDialog")
        #self.resize(1754, 3000)
        self.model = model


        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()
        self.createButtonBlock()
        #the top block is buttons to load setup xml and data files

        windowLayout.addWidget(self.ButtonBlock,2)
        #create some space between the buttons and xml setup block
        windowLayout.addStretch(1)

        #add the setup block
        self.createTopBlock()
        #the topBlock is hidden until we load or create a setup xml
        self.topBlock.setEnabled(False)
        windowLayout.addWidget(self.topBlock)
        #more space between component block
        windowLayout.addStretch(1)
        #TODO move to seperate file
        dlist = [
            [{'title': 'Time Unit', 'prompt': 'Select the units for the output time interval',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_time_units', 'name': 'outputTimeStepunit', 'folder': False},
             'Output Timestep'],

            [{'title': 'Output Timestep', 'prompt': 'Enter the output timestep',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'outputTimeStepvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Input Unit', 'prompt': 'Select the units for the input time interval',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_time_units', 'name': 'inputimeStepunit', 'folder': False},
             'Input Timestep'],

            [{'title': 'Input Timestep', 'prompt': 'Enter the input timestep',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'inputTimeStepvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Real Load Units', 'prompt': 'Select the units for the real load values.',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_load_units', 'name': 'realLoadChannelunit', 'folder': False},
             'Real Load'],
            [{'title': 'Real Load', 'prompt': 'Enter the name of the field real load values.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'realLoadChannelvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Time Series Date Format', 'prompt': 'Select the date format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_datetime_format', 'name': 'dateChannelformat', 'folder': False},
             'Time Series Date Column'],

            [{'title': 'Time Series Date Column', 'prompt': 'Enter the name of the field containing date data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'dateChannelvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Time Series Time Format', 'prompt': 'Select the time format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_datetime_format', 'name': 'timeChannelformat', 'folder': False},
             'Time Series Time Column'],

            [{'title': 'Time Series Time Column', 'prompt': 'Enter the name of the field containing time data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'timeChannelvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Raw Time Series', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'inputFileDir', 'folder': True}, 'Data Input Format'],

            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'hydroFileDir', 'folder': True}, 'Data Input Format'],

            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'windFileDir', 'folder': True}, 'Data Input Format'],

            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_data_format', 'name': 'inputFileFormat', 'folder': False},
             'Project'],

            [{'title': 'Project', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'project', 'folder': False}, None, ]

        ]

        self.WizardTree = self.buildWizardTree(dlist)

        # the bottom block is disabled until a setup file is created or loaded
        self.createTableBlock('Environment Data','environment',self.assignEnvironementBlock)
        self.environmentBlock.setEnabled(False)
        windowLayout.addWidget(self.environmentBlock)


        self.createTableBlock('Components', 'components', self.assignComponentBlock)
        self.componentBlock.setEnabled(False)

        windowLayout.addWidget(self.componentBlock)

        windowLayout.addStretch(2)
        #add a console window
        self.addConsole()
        windowLayout.addWidget(self.console)
        windowLayout.addStretch(2)
        windowLayout.addWidget(self.makeBlockButton(self.createInputFiles,'Create input files',None,'Create input files to run models'),3)
        #TODO get rid of test message
        self.console.showMessage("I am a console message")
        #set the main layout as the layout for the window
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Setup')

        #show the form
        self.showMaximized()

    # string, string ->
    def assignEnvironementBlock(self, value):
        self.environmentBlock = value
    def assignComponentBlock(self,value):
        self.componentBlock = value


    def addConsole(self):
        c = ConsoleDisplay()
        self.console = c
    #SetupForm -> QWidgets.QHBoxLayout
    #creates a horizontal button layout to insert in SetupForm
    def createButtonBlock(self):
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        #layout object name
        hlayout.setObjectName('buttonLayout')
        #add the button to load a setup xml

        hlayout.addWidget(self.makeBlockButton(self.functionForLoadButton,
                                 'Load Existing Project', None, 'Load a previously created project files.'))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            self.makeBlockButton(self.functionForCreateButton,
                                 'Create setup XML', None, 'Start the setup wizard to create a new setup file'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)
        #hlayout.addWidget(self.makeBlockButton(self.functionForExistingButton,
        #                         'Load Existing Project', None, 'Work with an existing project folder containing setup files.'))
        #hlayout.addWidget(self.makeBlockButton(self.functionForButton,'hello',None,'You need help with this button'))
        hlayout.addStretch(1)
        self.ButtonBlock.setLayout(hlayout)

        self.ButtonBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.ButtonBlock.setMinimumSize(self.size().width(),self.minimumSize().height())
        return hlayout

    #SetupForm, method, String, String, String -> QtQidget.QPushButton
    #returns a button with specified text, icon, hint and connection to the specified function
    def makeBlockButton(self, buttonFunction, text = None, icon = None, hint = None):
        if text is not None:
            button = QtWidgets.QPushButton(text,self)
        else:

            button = QtWidgets.QPushButton(self)
            button.setIcon(button.style().standardIcon(getattr(QtWidgets.QStyle, icon)))
        if hint is not None:
            button.setToolTip(hint)
            button.setToolTipDuration(2000)
        button.clicked.connect(lambda: self.onClick(buttonFunction))

        return button
    #SetupForm, method
    #calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self,buttonFunction):
        buttonFunction()

    #SetupForm ->
    #method to modify SetupForm layout
    def functionForCreateButton(self):
        import os
        #make a database
        #s is the 1st dialog box for the setup wizard
        s = SetupWizard(self.WizardTree, model, self)
        #display collected data
        hasSetup = model.feedSetupInfo()

        #make an empty database with references
        dbHandler = SQLiteHandler('component_manager')
        dbHandler.makeDatabase()
        dbHandler.closeDatabase()


        self.fillData(model)

        if hasSetup:
            self.topBlock.setEnabled(True)
            self.environmentBlock.setEnabled(True)
            self.componentBlock.setEnabled(True)

    def functionForLoadButton(self):
        import os
        #launch file navigator
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", None, "*xml" )
        if (setupFile == ('','')) | (setupFile is None):
            return
        model.setupFolder = os.path.dirname(setupFile[0])
        self.model.componentFolder = os.path.join(self.model.setupFolder,'../Components' )
        self.model.projectFolder = os.path.join(self.model.setupFolder, '../../')
        #TODO look for a saved component manager database to replace the default one

        model.project = os.path.basename(setupFile[0][:-9])

        #assign information to data model
        model.feedSetupInfo()
        #display data
        self.fillData(model)
        #TODO look for descriptor files and load those too
        self.topBlock.setEnabled(True)
        self.environmentBlock.setEnabled(True)

        self.componentBlock.setEnabled(True)
        print('Loaded %s:' % model.project)

    #TODO make dynamic from list input
    def buildWizardTree(self, dlist):
        # w1 = WizardTree(dlist[0][0], dlist[0][1], 0, [])  # output timestep unit
        # w2 = WizardTree(dlist[1][0], dlist[1][1], 4, [w1])  # output timestep value
        #
        # w3 = WizardTree(dlist[2][0], dlist[2][1], 0, [])  # input units
        # w4 = WizardTree(dlist[3][0], dlist[3][1], 3, [w3])  # input value
        #
        # w5 = WizardTree(dlist[4][0], dlist[4][1], 0, [])  # load units
        # w6 = WizardTree(dlist[5][0], dlist[5][1], 2, [w5])  # load column
        #
        # w7 = WizardTree(dlist[6][0], dlist[6][1], 0, [])  # Date Format
        # w8 = WizardTree(dlist[7][0], dlist[7][1], 1, [w7])  # Date Column

        # w9 = WizardTree(dlist[8][0], dlist[8][1], 0, [])  # Time Format
        # w10 = WizardTree(dlist[9][0], dlist[9][1], 0, [w9])  # Time Column

        #w11 = WizardTree(dlist[10][0], dlist[10][1], 2, [w10, w8, w6, w4, w2])  # Time Series
        w11 = WizardTree(dlist[10][0], dlist[10][1], 2, [])
        w12 = WizardTree(dlist[11][0], dlist[11][1], 1, [])  # hydro
        w13 = WizardTree(dlist[12][0], dlist[12][1], 0, [])  # wind

        w14 = WizardTree(dlist[13][0], dlist[13][1], 0, [w12, w11, w13])  # inputFileFormat
        w15 = WizardTree(dlist[14][0], dlist[14][1], 0, [w14])
        return w15


    #SetupForm -> SetupForm
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
                                    'Units':{'widget':'combo','items':['Seconds','Minutes','Hours'],'name':'inputTimeStepunit'}
                                   },
                          'Output':{'Value':{'widget':'txt','name':'outputTimeStepvalue'},
                                    'Units':{'widget':'combo','items':['Seconds','Minutes','Hours'],'name':'outputTimeStepunit'}}
                          }
        grid = setupGrid(g2)
        hlayout.addLayout(grid)

        #add another stretch to keep the grids away from the right edge
        hlayout.addStretch(1)
        
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


        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        fn(gb)
        return tv


    def functionForLoadDescriptor(self):

        print('load descriptor from xml')
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


    def functionForNewRecord(self, table):
        #add an empty record to the table

        #get the model
        tableView= self.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        #insert an empty row as the last record
        print("New row added to %s" %table)
        model.insertRows(model.rowCount(),1)
        model.submitAll()

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
                for r in selected:
                    model.removeRows(r.row(),1)
                # remove the xml files too
                handler = UIToHandler()
                print('deleting :%s' %model.data(model.index(r.row(),3)))
                handler.removeDescriptor(model.data(model.index(r.row(),3)),self.model.componentFolder)
                #Delete the record from the database and refresh the tableview
                model.submitAll()
                model.select()




    #string -> QGroupbox
    def dataButtons(self,table):
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()

        if table == 'components':

            buttonRow.addWidget(self.makeBlockButton(self.functionForLoadDescriptor,
                                               None, 'SP_DialogOpenButton', 'Load a previously created component xml file.'))

        buttonRow.addWidget(self.makeBlockButton(lambda:self.functionForNewRecord(table),
                                             '+', None,
                                             'Add a component'))
        buttonRow.addWidget(self.makeBlockButton(lambda:self.functionForDeleteRecord(table),
                                             None, 'SP_TrashIcon',
                                             'Delete a component'))
        buttonRow.addStretch(3)
        buttonBox.setLayout(buttonRow)
        return buttonBox

    #inserts data from the data model into corresponding boxes on the screen
    #SetupInfo -> None
    def fillData(self,model):
        from ComponentSQLiteHandler import SQLiteHandler
        d = model.getSetupTags()

        #for every key in d find the corresponding textbox or combo box

        for k in d.keys():

            for a in d[k]:

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
        # for headers, componentnames, componentattributes data goes into the database for table models
        for i in range(len(model.headerName.value)):
            print(model.headerName.value)
            print(model.componentName.value)
            dbHandler = SQLiteHandler('component_manager')
            fields = ('original_field_name','component_name','attribute','units')
            if (getDefault(model.headerName.value,i) != 'None'):
                values = (getDefault(model.headerName.value,i), getDefault(model.componentName.value,i),
                      getDefault(model.componentAttribute.value,i), getDefault(model.componentAttribute.unit,i))

                print(values)
                if getDefault(model.componentAttribute.value,i) in ['WS','WF','IR','Tamb','Tstorage']:
                    #insert into environment table
                    table = 'environment'
                else:
                     table = 'components'
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
    #send input data to the SetupInformation data model
    def sendData(self):
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
        model.headerNamevalue =[]
        model.componentNamevalue = []
        model.componentAttributevalue = []
        model.componentAttributeunit = []
        model.componentNames = []
        model.componentNamesvalue= []
        for i in range(0,componentModel.rowCount()):
            model.componentNamesvalue.append(componentModel.data(componentModel.index(i,3)))
            model.headerNamevalue.append(componentModel.data(componentModel.index(i,1)))
            model.componentNamevalue.append(componentModel.data(componentModel.index(i,3)))
            model.componentAttributevalue.append(componentModel.data(componentModel.index(i,7)))
            model.componentAttributeunit.append(componentModel.data(componentModel.index(i,4)))
        #and the same data from the environment section
        envView = self.findChild((QtWidgets.QTableView), 'environment')
        envModel = componentView.model()
        for i in range(0, envModel.rowCount()):
            model.headerNamevalue.append(componentModel.data(componentModel.index(i, 1)))
            model.componentNamevalue.append(componentModel.data(componentModel.index(i, 2)))
            model.componentAttributevalue.append(componentModel.data(componentModel.index(i, 3)))
            model.componentAttributeunit.append(componentModel.data(componentModel.index(i, 6)))
    #write data to the data model and generate input xml files for setup and components
    def createInputFiles(self):
        self.sendData()
        # write all the xml files

        #then component descriptors
        componentView = self.findChild((QtWidgets.QTableView), 'components')
        componentModel = componentView.model()
        listOfComponents = []

        #every row adds a component to the list
        for i in range(0, componentModel.rowCount()):
            newComponent = Component(component_name=componentModel.data(componentModel.index(i, 3)),
                                     original_field_name=componentModel.data(componentModel.index(i, 1)),
                                     units=componentModel.data(componentModel.index(i, 4)),
                                     offset=componentModel.data(componentModel.index(i, 6)),
                                     type=componentModel.data(componentModel.index(i, 2)),
                                     attribute=componentModel.data(componentModel.index(i, 7)),
                                     scale=componentModel.data(componentModel.index(i, 5)),
                                     pinmaxpa=componentModel.data(componentModel.index(i, 8)),
                                     poutmaxpa=componentModel.data(componentModel.index(i, 9)),
                                     qoutmaxpa=componentModel.data(componentModel.index(i,10)),
                                     isvoltagesource=componentModel.data(componentModel.index(i, 11)),
                                     tags=componentModel.data(componentModel.index(i, 12))
                                     )
            listOfComponents.append(newComponent)

        self.model.components = listOfComponents
        # start with the setupxml
        self.model.writeNewXML()
        # import datafiles
        # fix bad data and generate netcdf files
        return

    def readInDescriptors(self):
        #descriptors is a list of component soup objects used to fill the component model
        handler = UIToHandler()
        descriptors = handler.findDescriptors(self.model.componentFolder)

        #fill the form model with data in descriptors
        # for soup in descriptors:
        #     populateModel(soup)
        return len(descriptors)

    def closeEvent(self, event):
        import os
        import shutil
        print('Setup Form closing')

        #move the default database to the project folder and save xmls
        if 'projectFolder' in self.model.__dict__.keys():
            # on close save the xml files
            self.sendData()
            self.model.writeNewXML()
            path = os.path.dirname(__file__)
            shutil.move(os.path.join(path, 'component_manager'), os.path.join(self.model.projectFolder, 'component_manager'))
        else:
            #if a project was never set then just close and remove the default database
            os.remove('component_manager')