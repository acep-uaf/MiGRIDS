#subclass of QTableView for displaying component information
from PyQt5 import QtWidgets, QtSql, QtCore
class RunTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #TODO set delegates

class RunTableModel(QtSql.QSqlQueryModel):
    def __init__(self, parent):

        QtSql.QSqlQueryModel.__init__(self, parent)

        self.header = ['set',
                'run',
                'component',
                'tag',
                       'value']
        runQuery = QtSql.QSqlQuery("""SELECT set_name, run_name, component, change_tag, to_value value FROM sets JOIN runs on sets._id = runs.set_id

""")
        self.setQuery(runQuery)



    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


