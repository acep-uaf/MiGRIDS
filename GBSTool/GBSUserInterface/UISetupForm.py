
from PyQt5 import QtCore, QtGui, QtWidgets 
from gridLayoutSetup import setupGrid


class SetupForm(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        self.setObjectName("setupDialog")
        self.resize(1754, 1250)
        

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()
        self.createButtonBlock()
        #the top block is buttons to load setup xml and data files
        windowLayout.addWidget(self.ButtonBlock)
        #create some space between the buttons and xml setup block
        windowLayout.addStretch(1)
        #add the setup block
        self.createTopBlock()
        windowLayout.addWidget(self.horizontalGroupBox)
        #more space between component block
        windowLayout.addStretch(2)
        windowLayout.addWidget(self.createBottomBlock())
        #set the main layout as the layout for the window
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Setup')    
        #TODO add slider bars
        #connect slots so we can do something with these data
        QtCore.QMetaObject.connectSlotsByName(self)
        #show the form
        self.show()
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
        hlayout.addWidget(QtWidgets.QPushButton('Load TimeSeries', self))
        #force the buttons to the left side of the layout
        hlayout.addStretch(3)
        self.ButtonBlock.setLayout(hlayout)
        return hlayout
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
                          'columnWidths': [2, 1, 1],
                          'Input':{'Value':{'widget':'txt'},
                                           'Units':{'widget':'combo','items':['Seconds','Minutes','Hours']}},
                          'Output':{'Value':{'widget':'txt'},
                                           'Units':{'widget':'combo','items':['Seconds','Minutes','Hours']}}
                          }
        grid = setupGrid(g2)
        hlayout.addLayout(grid)
        #New
        #add another stretch to keep the grids away from the right edge
        hlayout.addStretch(2)
        
        self.horizontalGroupBox.setLayout(hlayout)
    #returns a table view
    def createBottomBlock(self):
        t = ComponentTableView(self)
        m = TableModel(self)
        t.setModel(m)
        #t.setAlternatingRowColor(True)
        for row in range(0,m.rowCount()):
            t.openPersistentEditor(m.index(row,1))
        return t
        
    #SetupForm -> SetupForm
    #creates gridlayout for entering component descriptor information
    # def createBottomBlock(self):
    #
    #     component_type = ['windturbine','windspeed','diesel generator',
    #                                        'hydrokinetic generator','water speed']
    #     attributes = ['P','WS','HS']
    #     units = ['W','KW','MW','m/s','mph','knots','km/h']
    #
    #     #returns a grid layout
    #     g1 = {'headers':['row name','Field Name',1,2,'Component Type','Attribute','Component Name', 'Units',
    #                      'Scale', 'P in Max Pa', 'Q in Max Pa', 'Q out Max Pa', 'Voltage Source'],
    #                       'rowNames':[1],
    #                       'columnWidths':[0,2,1,1,2,1,2,1,1,1,1,1,1],
    #                       1:{
    #                          'Field Name':{'widget':'txt','wscale':2},
    #                          1:{'widget':'btn','icon':'SP_DialogOpenButton'},
    #                          2:{'widget': 'btn','icon':'SP_TrashIcon'},
    #                          'Component Type':{'widget':'combo','items':component_type,'wscale':2},
    #                          'Attribute':{'widget':'combo','items':attributes},
    #                          'Component Name':{'widget':'lbl','wscale':2},
    #                          'Units':{'widget':'combo','items':units},
    #                          'Scale':{'widget':'txt'},
    #                          'P in Max Pa':{'widget':'txt'},
    #                          'Q in Max Pa': {'widget': 'txt'},
    #                          'Q out Max Pa': {'widget': 'txt'},
    #                          'Voltage Source':{'widget': 'chk'}
    #                           }
    #           }
    #     grid = setupGrid(g1)
    #     return grid

class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)

        self.setItemDelegateForColumn(1, ComboDelegate(self))
class ComboDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent):
            QtWidgets.QItemDelegate.__init__(self,parent)

    def createEditor(self,parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        li = ['left','right']
        for i in li:
            combo.addItem(i)
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        #combo.activated.connect(combo,QtCore.SIGNAL("currentIndexChanged(int)"), self, QtCore.SLOT("currentIndexChanged()"))
        return combo
    def setEditorData(selfself, editor, index):
        editor.blockSignals(True)
        editor.setCurrentIndex(int(index.model().data(index)))
        editor.blockSignals(False)
    def setModelData(self,editor, model, index):
        model.setData(index, editor.currentIndex())
    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        print(self.sender())
        self.commitData(self.sender())


class TableModel(QtCore.QAbstractTableModel):
    def rowCount(self, parent = QtCore.QModelIndex()):
        return 2
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 3
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid:
            return None
        if not role==QtCore.Qt.DisplayRole:
            return None
        return"{0:02d}".format(index.row())
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        print("setData", index.row(), index.column(), value)
        return int(value)
    def flags(self, index):
        if (index.column() == 0):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled

    # creates table of component attributes

