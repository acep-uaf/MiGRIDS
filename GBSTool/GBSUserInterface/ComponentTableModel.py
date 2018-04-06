from PyQt5 import QtCore, QtGui, QtWidgets
from ComponentSQLiteHandler import SQLiteHandler
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

class ComboReference():
    def __init__(self,cmb,table,db):
        self.cmb = cmb
        self.table = table
        self.db = db
        self.values = self.getValues()
        self.valueCodes = self.getCodes()

    def getValues(self):
        values = self.db.getRefInput(self.table)
        return values
    def getCodes(self):
        return [self.parseCombo(x) for x in self.values]
    def parseCombo(self, inputString):
        code = inputString.split(" - ")[0]
        description = inputString.split(" - ")[1]
        return code, description

    def valuesAsDict(self):

        d={}
        for v in self.values:
            code,description = self.parseCombo(v)
            d[code]=description

        return d
#LineEdit textbox connected to the table
class TextDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent):
        QtWidgets.QItemDelegate.__init__(self,parent)

    def createEditor(self,parent, option, index):
        txt = QtWidgets.QLineEdit(parent)
        txt.inputMethodHints()
        txt.textChanged.connect(self.currentIndexChanged)
        return txt
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

#Button  connected to the table
class ButtonDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent,icon):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.icon = icon
    def createEditor(self,parent, option, index):
        button = QtWidgets.QPushButton(parent)
        button.setIcon(button.style().standardIcon(getattr(QtWidgets.QStyle, self.icon)))
        button.clicked.connect(self.currentIndexChanged)
        return button
    def setModelData(self, editor, model, index):
        model.setData(index, editor.icon())

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

#Button  connected to the table
class ComboDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent,values):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.values = values

    def createEditor(self,parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.addItems(self.values)
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)

        #set the combo to the selected index

        editor.setCurrentIndex(int(index.model().data(index)))
        editor.blockSignals(False)

    #write model data
    def setModelData(self,editor, model, index):

        model.setData(index, editor.itemText(editor.currentIndex()))


    @QtCore.pyqtSlot()
    def currentIndexChanged(self):

        self.commitData.emit(self.sender())

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
            print(v)
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
        print("setData", index.row(), index.column(), value)
        return str(value)

    #index -> ItemEnabled
    def flags(self, index):
        if (index.column() == 0):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled