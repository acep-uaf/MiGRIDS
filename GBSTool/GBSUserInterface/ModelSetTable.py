from PyQt5  import QtWidgets, QtSql, QtCore
from Delegates import ComponentFormOpenerDelegate, TextBoxWithClickDelegate
#subclass of QTableView for displaying set information
class SetTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #text columns
        t_boxes = [1,2,3,]

        #for i in t_boxes:
        self.setItemDelegateForColumn(2, TextBoxWithClickDelegate(self, None))


class SetTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID','Set', 'Components', 'Runs']

        self.setTable('sets')

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


