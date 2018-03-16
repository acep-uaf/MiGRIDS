
from PyQt5 import QtCore, QtGui, QtWidgets
import ComponentTableModel as T
from gridLayoutSetup import setupGrid
from SetupWizard import SetupWizard

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
        windowLayout.addWidget(self.horizontalGroupBox)
        #more space between component block
        windowLayout.addStretch(1)

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

        #add a button to load the time series data
        hlayout.addWidget(QtWidgets.QPushButton('Create setup XML', self))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)
        hlayout.addWidget(QtWidgets.QPushButton("Load existing project",self))
        hlayout.addWidget(self.makeBlockButton(self.functionForButton,'hello',None,'You need help with this button'))
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
        wiz = SetupWizard({0:{'title':'Something Important', 'prompt':'enter something'},
                           1: {'title': 'Something Important1', 'prompt': 'enter something1'}})
        self.horizontalGroupBox.setVisible(False)


        #set up the signal and slot (make it do what it needs to do)
    def showWindow(self):
        print('showing')
        self.hide()
        self.show()

    #SetupForm -> SetupForm
    #creates a horizontal layout containing gridlayouts for data input
    def createTopBlock(self):
         #create a horizontal grouping to contain the top setup xml portion of the form
        self.horizontalGroupBox = QtWidgets.QGroupBox('Setup XML')
        
        #horizontalGroupBox = QtWidgets.QGroupBox('Setup XML')
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
        
        self.horizontalGroupBox.setLayout(hlayout)
        self.horizontalGroupBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.horizontalGroupBox.sizePolicy().retainSizeWhenHidden()

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
        







