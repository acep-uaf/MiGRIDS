from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from ComponentSQLiteHandler import SQLiteHandler
from Delegates import *
#subclass of QTableView for displaying component information
class EnvironmentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):

        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        t_boxes = [1, 4, 5,7, 8, 9]

        hidden = 0

        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        self.setColumnHidden(hidden, True)

        combos = [3,6]
        for c in combos:
            self.setItemDelegateForColumn(c,RelationDelegate(self))

#Tabel model to be displayed in component tableview
class EnvironmentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self,parent):
        QtSql.QSqlRelationalTableModel.__init__(self, parent)
        self.header = ['ID','Field','Component Name','Units','Scale',
                   'Offset','Attribute','Tags']

        self.setTable('environment')
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.setRelation(6, QtSql.QSqlRelation('ref_env_attributes', 'code', 'code'))
        self.setRelation(3, QtSql.QSqlRelation('ref_speed_units', 'code', 'code'))


        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

