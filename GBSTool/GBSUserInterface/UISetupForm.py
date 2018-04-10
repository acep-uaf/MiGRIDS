
from PyQt5 import QtCore, QtGui, QtWidgets
import ComponentTableModel as T
import EnvironmentTableModel as E
from gridLayoutSetup import setupGrid
from SetupWizard import SetupWizard
from WizardTree import WizardTree
from ConsoleDisplay import ConsoleDisplay
from SetupInformation import SetupInformation
from ComponentSQLiteHandler import SQLiteHandler

class SetupForm(QtWidgets.QWidget):
    global model
    model = SetupInformation()
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        self.setObjectName("setupDialog")
        self.resize(1754, 3000)
        self.model = model
        handler = SQLiteHandler('component_manager')
        handler.makeDatabase()
        handler.closeDatabase()

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
        self.topBlock.setVisible(False)
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
        #self.createEnvironmentBlock()
        #self.environmentBlock.setEnabled(False)
        #windowLayout.addWidget(self.environmentBlock)
        self.createBottomBlock()
        #the bottom block is disabled until a setup file is created or loaded
        self.bottomBlock.setEnabled(False)
        windowLayout.addWidget(self.bottomBlock)
        windowLayout.addStretch(2)
        #add a console window
        self.addConsole()
        windowLayout.addWidget(self.console)
        windowLayout.addStretch(2)
        #TODO get rid of test message
        self.console.showMessage("I am a console message")
        #set the main layout as the layout for the window
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Setup')

        #show the form
        self.showMaximized()
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
                                 'Load setup XML', None, 'Load a previously created setup xml file.'))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            self.makeBlockButton(self.functionForCreateButton,
                                 'Create setup XML', None, 'Start the setup wizard to create a new setup file'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)
        hlayout.addWidget(self.makeBlockButton(self.functionForExistingButton,
                                 'Load Existing Project', None, 'Work with an existing project folder containing setup files.'))
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
            button = QtWidgets.QPushButton(icon, self)
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
        #make a database

        #s is the 1st dialog box for the setup wizard
        s = SetupWizard(self.WizardTree, model, self)
        #display collected data
        hasSetup = model.feedSetupInfo()
        self.fillData(model)

        if hasSetup:
            self.topBlock.setVisible(True)
            self.environmentBlock.setEnabled(True)
            self.bottomBlock.setEnabled(True)

    def functionForLoadButton(self):
        import os
        #launch file navigator
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", None, "*xml" )
        if (setupFile == ('','')) | (setupFile is None):
            return
        model.setupFolder = os.path.dirname(setupFile[0])

        model.project = os.path.basename(setupFile[0][:-9])
        print(model.project)
        #assign information to data model
        model.feedSetupInfo()
        #display data
        self.fillData(model)
        self.topBlock.setVisible(True)
        #self.environmentBlock.setEnabled(True)

        self.bottomBlock.setEnabled(True)
    def functionForExistingButton(self):
        import os
        #launch folderdialog
        #set project name and read setup file
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", None,"*xml" )

        model.setupFolder = os.path.dirname(setupFile[0])
        #assign information to data model
        model.feedSetupInfo()
        #display data
        self.fillData(model)
        self.topBlock.setVisible(False)
    #TODO make dynamic from list input
    def buildWizardTree(self, dlist):
        w1 = WizardTree(dlist[0][0], dlist[0][1], 0, [])  # output timestep unit
        w2 = WizardTree(dlist[1][0], dlist[1][1], 4, [w1])  # output timestep value

        w3 = WizardTree(dlist[2][0], dlist[2][1], 0, [])  # input units
        w4 = WizardTree(dlist[3][0], dlist[3][1], 3, [w3])  # input value

        w5 = WizardTree(dlist[4][0], dlist[4][1], 0, [])  # load units
        w6 = WizardTree(dlist[5][0], dlist[5][1], 2, [w5])  # load column

        w7 = WizardTree(dlist[6][0], dlist[6][1], 0, [])  # Date Format
        w8 = WizardTree(dlist[7][0], dlist[7][1], 1, [w7])  # Date Column

        w9 = WizardTree(dlist[8][0], dlist[8][1], 0, [])  # Time Format
        w10 = WizardTree(dlist[9][0], dlist[9][1], 0, [w9])  # Time Column

        w11 = WizardTree(dlist[10][0], dlist[10][1], 2, [w10, w8, w6, w4, w2])  # Time Series
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
    #environment data is similar in layout to component descriptors but the info does not get written to descriptor files
    def createEnvironmentBlock(self):
    #returns a table view within a horizontal layout
        self.environmentBlock = QtWidgets.QGroupBox('Environmental Inputs')
        tableGroup = QtWidgets.QHBoxLayout()
        tv = E.EnvironmentTableView(self)

        m = E.EnvironmentTableModel(self)

        tv.setModel(m)

        for row in range(0, m.rowCount()):
            for c in range(0,m.columnCount()):
                tv.openPersistentEditor(m.index(row, c))

            tv.closePersistentEditor(m.index(row,4))

        tableGroup.addWidget(tv, 1)
        self.environmentBlock.setLayout(tableGroup)
        self.environmentBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return tv

    def createBottomBlock(self):
        self.bottomBlock = QtWidgets.QGroupBox('Components')
        tableGroup = QtWidgets.QHBoxLayout()
        tv = T.ComponentTableView(self)

        m = T.ComponentTableModel(self)

        tv.setModel(m)

        # for row in range(0, m.rowCount()):
        #     for c in range(0,m.columnCount()):
        #         tv.openPersistentEditor(m.index(row, c))
        #     # tv.closePersistentEditor(m.index(row,4))
        #     # tv.closePersistentEditor(m.index(row, 0))


        tableGroup.addWidget(tv,1)
        self.bottomBlock.setLayout(tableGroup)
        self.bottomBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return tv
        

    def fillData(self,model):
        d = model.getSetupTags()

        #for every key in d find the corresponding textbox or combo box
        for k in d.keys():

            for a in d[k]:

                edit_field = self.findChild((QtWidgets.QLineEdit,QtWidgets.QComboBox), k + a)

                if type(edit_field) is QtWidgets.QLineEdit:

                    edit_field.setText(d[k][a])
                elif type(edit_field) is QtWidgets.QComboBox:
                    edit_field.setCurrentIndex(edit_field.findText(d[k][a]))

        return
