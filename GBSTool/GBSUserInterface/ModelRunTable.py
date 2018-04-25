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

        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID','set',
                'run',
                'field1',
                'field2']

        self.setTable('runs')
        self.setFilter("set_id like '" + parent.currentset + "%'")
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


