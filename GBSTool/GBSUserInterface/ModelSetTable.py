from PyQt5  import QtWidgets, QtSql, QtCore
from Delegates import ComponentFormOpenerDelegate, TextBoxWithClickDelegate, TextDelegate
from Delegates import ComboDelegate
#subclass of QTableView for displaying set information
class SetTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        self.column1 = kwargs.get('column1')
        QtWidgets.QTableView.__init__(self, *args)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        self.setItemDelegateForColumn(1, TextDelegate(self))
        self.setItemDelegateForColumn(2,ComboDelegate(self))

class SetTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID','Set', 'Component', 'Tag', 'Value']

        self.setTable('sets')

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.setFilter('set_name = ' + self.column1)
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


