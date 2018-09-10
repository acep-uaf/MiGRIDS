
from GBSUserInterface.Delegates import *


#QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        # column 1 gets autfilled with filedir
        self.column1 = kwargs.get('column1')
        QtWidgets.QTableView.__init__(self, *args)


        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #text columns
        t_boxes = [1,2,6,7,]
        #for i in t_boxes:
         #   self.setItemDelegateForColumn(i, TextDelegate(self))
#this doesn't do anything here
        self.setColumnHidden(0, True)
        self.setColumnHidden(1, True)

        #combo columns
        self.setItemDelegateForColumn(1, TextDelegate(self))
        self.setItemDelegateForColumn(3,RelationDelegate(self,'component_type'))
        self.setItemDelegateForColumn(8, RelationDelegate(self, 'component_attribute'))
        self.setItemDelegateForColumn(5, RelationDelegate(self, 'component_units'))
        self.setItemDelegateForColumn(9,ComponentFormOpenerDelegate(self,'+'))

#data model to fill component table
class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)
        #values to use as headers for component table
        self.header = ['ID','Directory','Field', 'Type', 'Component Name', 'Units', 'Scale',
                    'Offset','Attribute','Tags']
        self.setTable('components')
        #leftjoin so null values ok
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        #set the dropdowns

        self.setRelation(3,QtSql.QSqlRelation('ref_component_type','code','code'))
        self.setRelation(8, QtSql.QSqlRelation('ref_attributes','code','code'))
        self.setRelation(5, QtSql.QSqlRelation('ref_power_units', 'code', 'code'))
        #database gets updated when fields are changed
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #select the data to display filtered to the input directory selected

        dirm = parent.FileBlock.findChild(QtWidgets.QWidget,'inputFileDirvalue').text()

        #self.setFilter('fileinputdir = ' + dirm)
        #self.setQuery(runQuery)
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


