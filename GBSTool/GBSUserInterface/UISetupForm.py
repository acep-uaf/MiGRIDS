
from PyQt5 import QtCore, QtGui, QtWidgets 
from gridLayoutSetup import setupGrid


class UISetup(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        self.setObjectName("setupDialog")
        self.resize(1754, 1250)
        

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()
        self.createButtonBlock()
        #the top block is the setup xml portion
        
        windowLayout.addWidget(self.ButtonBlock)
        windowLayout.addStretch(1)
        #add the horizontal block to the vertical layout
        self.createTopBlock()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addStretch(2)
        #windowLayout.addLayout(self.createBottomBlock())
        #make the vertical layout the main layout of the dialogwindow
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setLayout(windowLayout)
        
        self.setWindowTitle('Setup')    
        
        QtCore.QMetaObject.connectSlotsByName(self)
        #show the form
        self.show()
        
    def createButtonBlock(self):
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QPushButton('Load setup XML', self))
        
        hlayout.setObjectName('buttonLayout')
        hlayout.addWidget(QtWidgets.QPushButton('Load TimeSeries', self))
        hlayout.addStretch(3)
        self.ButtonBlock.setLayout(hlayout)
        return hlayout
    def createTopBlock(self):
         #create a horizontal grouping to contain the top setup xml portion of the form
        self.horizontalGroupBox = QtWidgets.QGroupBox('Setup XML')
        
        #horizontalGroupBox = QtWidgets.QGroupBox('Setup XML')
        hlayout = QtWidgets.QHBoxLayout()
        
        hlayout.setObjectName("layout1")
        
        #add the setup grids
        g1 = {'headers':['Attribute','Field','Format'],
                          'rowNames':['Date','Time','Load'],
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
                          'Input':{'Value':{'widget':'txt'},
                                           'Units':{'widget':'combo','items':['Seconds','Minutes','Hours']}},
                          'Output':{'Value':{'widget':'txt'},
                                           'Units':{'widget':'combo','items':['Seconds','Minutes','Hours']}}
                          }
        grid = setupGrid(g2)
        hlayout.addLayout(grid)
        
        
        self.horizontalGroupBox.setLayout(hlayout)
        
        
    def createBottomBlock(self):
        #returns a grid layout
        g1 = {'headers':['Attribute','Field','Format'],
                          'rowNames':['Date','Time','Load'],
                          'Date':{'Field':{'widget':'combo','items':['Date','Time','Wtg1']},
                                           'Format':{'widget':'combo','items':['ordinal']}},
                          'Time':{'Field':{'widget':'combo','items':['Date','Time','Wtg1']},
                                           'Format':{'widget':'combo','items':['excel']}},
                          'Load':{'Field':{'widget':'combo','items':['Date','Wtg1']},
                                           'Format':{'widget':'combo','items':['KW','W','MW']}}}
        grid = setupGrid(g1)
        return grid
