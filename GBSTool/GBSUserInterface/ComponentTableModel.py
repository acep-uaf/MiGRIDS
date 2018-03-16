from PyQt5 import QtCore, QtGui, QtWidgets
from ComponentSQLiteHandler import SQLiteHandler

class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        #attributes are column 8
        attributes = ['P', 'WS', 'HS']
        self.setItemDelegateForColumn(8, ComboDelegate(self,attributes))
        #types are column 3
        type_list = ['windturbine', 'windspeed', 'diesel generator', 'hydrokinetic generator','water speed']

        self.setItemDelegateForColumn(3,ComboDelegate(self,type_list))
        #units are in column 5
        units = ['W', 'KW', 'MW', 'm/s', 'mph', 'knots', 'km/h']
        self.setItemDelegateForColumn(5, ComboDelegate(self, units))
        #button to navigate to descriptor xml file is in column 0
        self.setItemDelegateForColumn(1,ButtonDelegate(self, 'SP_DialogOpenButton'))
        #button to delete a component is in column 2
        self.setItemDelegateForColumn(2, ButtonDelegate(self, 'SP_TrashIcon'))
        self.setItemDelegateForColumn(0, TextDelegate(self))

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
        editor.setCurrentIndex(int(index.model().data(index)))
        editor.blockSignals(False)

    def setModelData(self,editor, model, index):

        model.setData(index, editor.itemText(editor.currentIndex()))

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):

        self.commitData.emit(self.sender())

class ComponentTableModel(QtCore.QAbstractTableModel):
    def __init__(self,parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.db = SQLiteHandler("component_manager")
        self.header = self.getHeader(self.db)
    def rowCount(self, parent = QtCore.QModelIndex()):

        return self.db.getComponentTableCount() + 1
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 14
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid:
            return None
        if not role==QtCore.Qt.DisplayRole:
            return None
        return "{0:02d}".format(index.row())
    def getHeader(self,db):
        headers = db.getHeaders("components")
        print(headers)
        headers = ['Field',' ',' ','Type','Component Name','Units','Scale',
                   'Offset','Attribute','P in max pa','Q in max pa','Q out max pa','Voltage Source','Tags']
        return headers
    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        print("setData", index.row(), index.column(), value)
        return str(value)
    def flags(self, index):
        if (index.column() == 0):
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled