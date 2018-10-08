from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from GBSUserInterface.Delegates import *
#subclass of QTableView for displaying component information
class EnvironmentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        t_boxes = [1,2, 5, 6,8, 9, 10]

        hidden = 0

        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        self.setColumnHidden(hidden, True)

        #column 2 is the component name. Environment variables need to be tied to an existing component name
        combos = [3,4,7]
        for c in combos:
            self.setItemDelegateForColumn(c,RelationDelegate(self,None))

#Tabel model to be displayed in component tableview
class EnvironmentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self,parent):
        QtSql.QSqlRelationalTableModel.__init__(self, parent)
        self.header = ['ID','Directory','Field','Component Name','Units','Scale',
                   'Offset','Attribute','Tags']

        self.setTable('environment')
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.setRelation(7, QtSql.QSqlRelation('ref_env_attributes', 'code', 'code'))
        self.setRelation(4, QtSql.QSqlRelation('ref_speed_units', 'code', 'code'))
        self.setRelation(3, QtSql.QSqlRelation('components', 'component_name', 'component_name'))
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

