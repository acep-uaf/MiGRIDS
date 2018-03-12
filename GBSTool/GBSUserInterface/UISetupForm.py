import sys
from PyQt5 import QtCore, QtGui, QtWidgets 

def setupGrid(inputDictionary):
      def getColumn(objectName, row, c, gridLayout):
       o =gridLayout.itemAtPosition(0,c)
       if c > gridLayout.columnCount():
           return False
       if o is not None:
           o = o.widget()
           n = o.objectName()
           if n == objectName:
               return c
       return getColumn(objectName,row,c+1,gridLayout)
   
      def getWidget(stringType):
           choices={'combo':QtWidgets.QComboBox(),'txt':QtWidgets.QLineEdit()}
           result = choices.get(stringType,QtWidgets.QTextEdit())
           return result     
      font = QtGui.QFont()
      font.setPointSize(26)
             #grid block layout
      grid = QtWidgets.QGridLayout()
      grid.setContentsMargins(0, 0, 0, 0)
      grid.setObjectName("grdSetup")
            
      headers = inputDictionary['headers']
            
      for i in range(len(headers)):
         grid.lbl = QtWidgets.QLabel()        
         grid.lbl.setFont(font)
         grid.lbl.setObjectName('lbl' + headers[i])
         grid.addWidget(grid.lbl, 0, i, 1, 1)
         grid.lbl.setText(headers[i])
         rowNames = inputDictionary['rowNames']
            
      for i in range(len(rowNames)):
          grid.lbl = QtWidgets.QLabel()        
          grid.lbl.setFont(font)
          grid.lbl.setObjectName('lbl' + rowNames[i])
          grid.addWidget(grid.lbl, i+1, 0, 1, 1)
          grid.lbl.setText(rowNames[i])  
                
                #get the row of widgets
          r = inputDictionary[rowNames[i]]
                #there will be a value for every column except the first one
          for h in headers[1:]:
              grid.wid=getWidget(r[h]['widget'])
              grid.wid.setFont(font)
              grid.wid.setObjectName('inp'.join(r).join(h))
              grid.addWidget(grid.wid,i+1,getColumn('lbl' + h,i,1,grid),1,1)
              if 'items' in r[h].keys():
                  for item in r[h]['items']:
                      grid.wid.addItem(item)
                                   

      return grid

class UISetup(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        self.setObjectName("setupDialog")
        self.resize(1754, 1250)
        #TODO redo these siz policies
        #sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        #self.setSizePolicy(sizePolicy)
 
        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()
        #the top block is the setup xml portion
        self.createTopBlock()
        
        
        #add the horizontal block to the vertical layout
        windowLayout.addWidget(self.horizontalGroupBox)
       
        windowLayout.addLayout(self.createBottomBlock())
        #make the vertical layout the main layout of the dialogwindow
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setLayout(windowLayout)
        
        self.setWindowTitle('Setup')    
        
        QtCore.QMetaObject.connectSlotsByName(self)
        #show the form
        self.show()
        
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