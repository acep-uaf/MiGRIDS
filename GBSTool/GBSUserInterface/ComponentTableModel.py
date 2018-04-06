from PyQt5 import QtCore, QtGui, QtWidgets
from ComponentSQLiteHandler import SQLiteHandler
from Delegates import *

#subclass of QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        myHandler = SQLiteHandler('component_manager')
        #attributes are column 8
        self.attributes = ComboReference('component_attributes','ref_attributes',myHandler)
        self.setItemDelegateForColumn(8, ComboDelegate(self,self.attributes.values))
        #types are column 3
        self.component_type = ComboReference('component_type','ref_component_type',myHandler)
        self.setItemDelegateForColumn(3,ComboDelegate(self,self.component_type.values))
        self.units = ComboReference('load_units','ref_load_units',myHandler)

        self.setItemDelegateForColumn(5, ComboDelegate(self, self.units.values))
        #button to navigate to descriptor xml file is in column 0
        self.setItemDelegateForColumn(1,ButtonDelegate(self, 'SP_DialogOpenButton'))
        #button to delete a component is in column 2
        self.setItemDelegateForColumn(2, ButtonDelegate(self, 'SP_TrashIcon'))
        self.setItemDelegateForColumn(0, TextDelegate(self))
        #combos is the list of attributes that associated with combo boxes
        self.combos = [x for x in self.__dict__.keys() if type(self.__getattribute__(x)) == ComboReference]
        myHandler.closeDatabase()


#Tabel model to be displayed in component tableview
class ComponentTableModel(QtCore.QAbstractTableModel):
    def __init__(self,parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.db = SQLiteHandler("component_manager")
        self.header,self.columns = self.getHeader(self.db)

    #QModelIndex -> integer
    #returns the number of rows to display
    #number of rows equals the number of components + an empty row
    def rowCount(self, parent = QtCore.QModelIndex()):

        return self.db.getComponentTableCount() + 1

    # QModelIndex -> integer
    #returns the number of columns to display
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 14

    # index, Qt.DisplayRole -> String
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid:
            return None
        if not role==QtCore.Qt.DisplayRole:
            return None

        v = self.db.getComponentData(self.columns[index.column()],index.row())

        #if its feeding a combo box get the list position
        if self.db.hasRef(self.columns[index.column()]):
            rvalues = self.db.getCodes(self.db.getRef(self.columns[index.column()]))

            #select the matching combo
            v = [i for i,x in enumerate(rvalues) if x == v]
            if len(v)>0:
                v = v[0]
            else:
                v = 0

        return v

    #SQLitedatbase connection -> listOfStrings
    def getHeader(self,db):

        #columnNames = db.getHeaders("components")

        headers = ['Field',' ',' ','Type','Component Name','Units','Scale',
                   'Offset','Attribute','P in max pa','Q in max pa','Q out max pa','Voltage Source','Tags']
        columnNames = ['original_field_name','','','component_type', 'component_name', 'units', 'scale',
                       'offset', 'attribute', 'p_in_maxpa', 'q_in_maxpa', 'q_out_maxpa', 'is_voltage_source', 'tags']
        return headers, columnNames

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

    #index, string, DisplayRole -> string
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):

        #atleast the first column, the third column and the 4 column must be set to write the component
        print('index column %s' %index.column())
        if index.column() in [0,3]:
            print('Required')
            check1 = self.index(index.row(),0)
            check2 = self.index(index.row(),3)
            if self.missingData(check1) | self.missingData(check2):
                return
        print("setData", index.row(), index.column(), value)
        #find the table parameter that changed
        #write that parameter to the corresponding component
        return str(value)
    def missingData(self,index):
        print('data is %s' %str(self.data(index)))
        if (self.data(index) == 0) | (self.data(index) == ''):
            print('missing')
            return True
        return False

    #index -> ItemEnabled
    def flags(self, index):
        if (index.column() == 0):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled