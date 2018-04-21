#subclass of QTableView for displaying component information
from PyQt5 import QtWidgets, QtSql, QtCore
class RunTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #TODO set delegates

class RunTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent):
        import os
        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID']

        self.setTable('runtable')
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


