from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from ComponentSQLiteHandler import SQLiteHandler
from Delegates import *
#subclass of QTableView for displaying component information
class EnvironmentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):

        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        t_boxes = [1, 2, 4, 5, 7, 8, 9]

        hidden = 0

        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        self.setColumnHidden(hidden, True)
        self.setItemDelegateForColumn(2, QtSql.QSqlRelationalDelegate(self))


#Tabel model to be displayed in component tableview
class EnvironmentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self,parent):
        QtSql.QSqlRelationalTableModel.__init__(self, parent)
        self.header = ['ID','Field','Attribute','Component Name','Units','Scale',
                   'Offset','Tags']

        self.setTable('environment')
        self.setRelation(2, QtSql.QSqlRelation('ref_component_type', 'code', 'code'))

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

