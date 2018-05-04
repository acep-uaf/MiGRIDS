from PyQt5  import QtWidgets, QtSql, QtCore
from Delegates import TextDelegate
from Delegates import ComboDelegate
#subclass of QTableView for displaying set information
class SetTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        self.column1 = kwargs.get('column1')
        QtWidgets.QTableView.__init__(self, *args)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        def makeComponentList():
            import pandas as pd
            from ProjectSQLiteHandler import ProjectSQLiteHandler
            sqlhandler = ProjectSQLiteHandler('project_manager')
            components = pd.read_sql_query("select component_name from components", sqlhandler.connection)

            components = list(components['component_name'])
            sqlhandler.closeDatabase()
            return components

        values = QtCore.QStringListModel(makeComponentList())
        attributes = QtCore.QStringListModel([])
        self.setItemDelegateForColumn(1, TextDelegate(self))
        self.setItemDelegateForColumn(2,ComboDelegate(self,values,'componentName'))

        #attributes (column 3)get updated when component Name gets selected (column 2)
        self.setItemDelegateForColumn(3, ComboDelegate(self, attributes,'componentAttribute'))

class SetTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)

        self.header = ['ID','Set', 'Component', 'Tag', 'Value']

        self.setTable('sets')

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #the set table gets filtered to only show records for that set
        self.setFilter('set_name = ' + parent.set)
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


