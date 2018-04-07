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
        self.attributes = ComboReference('component_attributes',['ref_attributes'],myHandler)
        self.setItemDelegateForColumn(8, ComboDelegate(self,self.attributes.values))
        #types are column 3
        self.component_type = ComboReference('component_type',['ref_component_type'],myHandler)
        self.setItemDelegateForColumn(3,ComboDelegate(self,self.component_type.values))
        self.units = ComboReference('load_units',['ref_load_units'],myHandler)
        self.tf = ComboReference('isVoltage',['ref_true_false'],myHandler)
        self.setItemDelegateForColumn(12, ComboDelegate(self, self.tf.values))

        self.setItemDelegateForColumn(5, ComboDelegate(self, self.units.values))
        #button to navigate to descriptor xml file is in column 0
        self.setItemDelegateForColumn(1,ButtonDelegate(self, 'SP_DialogOpenButton'))
        #button to delete a component is in column 2
        self.setItemDelegateForColumn(2, ButtonDelegate(self, 'SP_TrashIcon'))
        t_boxes = [0,4,6,7,9,10,11,13]
        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        #combos is the list of attributes that associated with combo boxes
        self.combos = [x for x in self.__dict__.keys() if type(self.__getattribute__(x)) == ComboReference]
        myHandler.closeDatabase()


#Tabel model to be displayed in component tableview
class ComponentTableModel(QtCore.QAbstractTableModel):
    def __init__(self,parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.db = SQLiteHandler("component_manager")
        print(str(self.db.getComponentTableCount()))
        self.header,self.columns = self.getHeader(self.db)

    #QModelIndex -> integer
    #returns the number of rows to display
    #number of rows equals the number of components + an empty row
    def rowCount(self, parent = QtCore.QModelIndex()):

        return self.db.getComponentTableCount() + 1

    # QModelIndex -> integer
    #returns the number of columns to display
    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self.columns)

    # index, Qt.DisplayRole -> String
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid:
            return None
        if not role==QtCore.Qt.DisplayRole:
            return None

        v = self.db.getComponentData(self.columns[index.column()],index.row())
        if v is None:
            v = ''
        #if its feeding a combo box get the list position
        if self.db.hasRef(self.columns[index.column()]):
            rvalues = self.db.getCodes(self.db.getRef(self.columns[index.column()]))

            #select the matching combo

            v = [i for i,x in enumerate(rvalues) if x == v]
            #TODO change this so code list includes empty first position then we don't need to add 1 and position will be correct for coombined reference tables
            # add 1 to account for empty first position in combo boxes
            if len(v)>0:
                v = v[0] +1
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
    #index -> string
    def makeComponentName(self,index):
        #get the component type
        print('index row is: %s' %str(index.row()))
        print('index column is: %s' % str(index.column()))
        componentType = self.data(self.index(index.row(), 3))
        print('component type: %s' %componentType)

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

    #index, string, DisplayRole -> string
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        #atleast the first column, the third column and the 4 column must be set to write the component

        if index.column() in [0,3]:
            check1 = self.index(index.row(),0)
            check2 = self.index(index.row(),3)
            if self.missingData(check1) | self.missingData(check2):
                print(self.missingData(check1))
                print(self.missingData(check2))
                #Don't do anything if required data is still missing
                return
            else:
                component = self.data(self.index(index.row(), 4))
                print('component:%s' % component)
                if component == 0:
                    print("component name isn't set")
                    self.makeComponentName(index)
                    # component = self.data(self.index(index.row(),4))

        print("setData", index.row(), index.column(), value)
        #find the table parameter that changed
        tag = self.columns[index.column()]


        #write that parameter to the corresponding component
        #writeComponentTag(tag,component,value)
        return True

    def missingData(self,index):
        print('missing data row index %s'%str(index.row()))
        print('missing data column index %s' % str(index.column()))
        print('mising data value %s' %str(self.data(index)))
        #if a combobox is set to 0 or a text field is an empty string then the data is missing
        if (self.data(index) == 0) | (self.data(index) == ''):
            return True
        return False

    #index -> Boolean
    def flags(self, index):
        # if (index.column() == 0):
        #     return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        # else:
        #     return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled