from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from ProjectSQLiteHandler import ProjectSQLiteHandler
from Delegates import *

#subclass of QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #text columns
        t_boxes = [1,5,6,]
        #columns to hide
        hidden = 0

        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))

        self.setColumnHidden(0, True)
        #combo columns
        combos = [2,4,7]
        for c in combos:
            self.setItemDelegateForColumn(c,RelationDelegate(self))
        self.setItemDelegateForColumn(8,ComponentFormOpenerDelegate(self,'+'))

class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):
        import os
        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID','Field', 'Type', 'Component Name', 'Units', 'Scale',
                    'Offset','Attribute','Tags']

        self.setTable('components')
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.setRelation(2,QtSql.QSqlRelation('ref_component_type','code','code'))
        self.setRelation(7, QtSql.QSqlRelation('ref_attributes','code','code'))
        self.setRelation(4, QtSql.QSqlRelation('ref_power_units', 'code', 'code'))

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


