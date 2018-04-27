from PyQt5  import QtWidgets, QtSql, QtCore
from Delegates import ComponentFormOpenerDelegate, TextBoxWithClickDelegate
from Delegates import ComboDelegate
#subclass of QTableView for displaying set information
class SetTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        #self.setItemDelegateForColumn(2, TextBoxWithClickDelegate(self, None))
        self.setItemDelegateForColumn(2,ComboDelegate(self))

class SetTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID','Set', 'Component', 'Tag', 'Value']

        self.setTable('sets')

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


