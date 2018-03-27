
from PyQt5 import QtCore, QtGui, QtWidgets
import ComponentTableModel as T
from gridLayoutSetup import setupGrid
from SetupWizard import SetupWizard
from WizardTree import WizardTree

class SetupForm(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        self.setObjectName("setupDialog")
        self.resize(1754, 1200)
        

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()
        self.createButtonBlock()
        #the top block is buttons to load setup xml and data files
        #TODO each added widget needs to be set to max extent
        windowLayout.addWidget(self.ButtonBlock,2)
        #create some space between the buttons and xml setup block
        windowLayout.addStretch(1)

        #add the setup block
        self.createTopBlock()
        windowLayout.addWidget(self.topBlock)
        #more space between component block
        windowLayout.addStretch(1)
        dlist = [
            [{'title': 'Time Series Date Format', 'prompt': 'Select the date format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Raw Time Series', 0, []],
            [{'title': 'Raw Time Series', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 2, [0]],
            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 1, []],
            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 0, []],
            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Project Name', 0, [1, 2, 3]],
            [{'title': 'Project Name', 'prompt': 'Enter the name of your project'}, None, 0, [4]]

        ]
        self.WizardTree = self.buildWizardTree(dlist)
        self.createBottomBlock()
        windowLayout.addWidget(self.bottomBlock)

        #set the main layout as the layout for the window
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Setup')

        #show the form
        self.showMaximized()

    #SetupForm -> QWidgets.QHBoxLayout
    #creates a horizontal button layout to insert in SetupForm
    def createButtonBlock(self):
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        #layout object name
        hlayout.setObjectName('buttonLayout')
        #add the button to load a setup xml

        hlayout.addWidget(QtWidgets.QPushButton('Load setup XML', self))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            self.makeBlockButton(self.functionForButton,
                                 'Create setup XML', None, 'Start the setup wizard to create a new setup file'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)
        hlayout.addWidget(QtWidgets.QPushButton("Load existing project",self))
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
    def functionForButton(self):
        #s is the 1st dialog box for the setup wizard
        s = SetupWizard(self.WizardTree)
        self.topBlock.setVisible(False)

    #TODO make dynamic from list input
    def buildWizardTree(self, dlist):
        w1 = WizardTree(dlist[0][0], dlist[0][1], dlist[0][2], [])
        w2 = WizardTree(dlist[1][0], dlist[1][1], dlist[1][2], [w1])
        w3 = WizardTree(dlist[2][0], dlist[2][1], dlist[2][2], [])
        w4 = WizardTree(dlist[3][0], dlist[3][1], dlist[3][2], [])
        w5 = WizardTree(dlist[4][0], dlist[4][1], dlist[4][2], [w2, w3, w4])
        w6 = WizardTree(dlist[5][0], dlist[5][1], dlist[5][2], [w5])
        return w6

    def showWindow(self):
        self.hide()
        self.show()

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
                          'Date':{'Field':{'widget':'combo','items':['Date','Time','Wtg1']},
                                           'Format':{'widget':'combo','items':['ordinal']}},
                          'Time':{'Field':{'widget':'combo','items':['Date','Time','Wtg1']},
                                           'Format':{'widget':'combo','items':['excel']}},
                          'Load':{'Field':{'widget':'combo','items':['Date','Wtg1']},
                                           'Format':{'widget':'combo','items':['KW','W','MW']}}}
        grid = setupGrid(g1)
        hlayout.addLayout(grid)
        hlayout.addStretch(1)    
        #add the second grid
        g2 = {'headers':['TimeStep','Value','Units'],
                          'rowNames':['Input','Output'],
                          'columnWidths': [1, 1, 1],
                          'Input':{'Value':{'widget':'txt'},
                                           'Units':{'widget':'combo','items':['Seconds','Minutes','Hours']}},
                          'Output':{'Value':{'widget':'txt'},
                                           'Units':{'widget':'combo','items':['Seconds','Minutes','Hours']}}
                          }
        grid = setupGrid(g2)
        hlayout.addLayout(grid)

        #add another stretch to keep the grids away from the right edge
        hlayout.addStretch(1)
        
        self.topBlock.setLayout(hlayout)
        self.topBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.topBlock.sizePolicy().retainSizeWhenHidden()

    #returns a table view within a horizontal layout
    def createBottomBlock(self):
        self.bottomBlock = QtWidgets.QGroupBox('Descriptor XML')
        tableGroup = QtWidgets.QHBoxLayout()
        tv = T.ComponentTableView(self)

        m = T.ComponentTableModel(self)

        tv.setModel(m)

        for row in range(0,m.rowCount()):
            tv.openPersistentEditor(m.index(row,3))
            tv.openPersistentEditor(m.index(row,8))
            tv.openPersistentEditor(m.index(row,5))
            tv.openPersistentEditor(m.index(row,1))
            tv.openPersistentEditor(m.index(row,2))
            tv.openPersistentEditor(m.index(row,0))

            # for c in range(0,4):
            #     tv.openPersistentEditor(m.index(row,c))
            # for c in range(5,14):
            #     tv.openPersistentEditor(m.index(row, c))

        tableGroup.addWidget(tv,1)
        self.bottomBlock.setLayout(tableGroup)
        self.bottomBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return tv
        



