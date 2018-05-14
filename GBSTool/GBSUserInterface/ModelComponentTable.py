
from Delegates import *

#QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        self.column3 = kwargs.get('column3')
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #text columns
        t_boxes = [1,5,6,]
        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        TextDelegate
        self.setColumnHidden(0, True)

        #combo columns
        self.setItemDelegateForColumn(2,RelationDelegate(self,'component_type'))
        self.setItemDelegateForColumn(7, RelationDelegate(self, 'component_attribute'))
        self.setItemDelegateForColumn(4, RelationDelegate(self, 'component_units'))
        self.setItemDelegateForColumn(8,ComponentFormOpenerDelegate(self,'+'))

#data model to fill component table
class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)
        #values to use as headers for component table
        self.header = ['ID','Field', 'Type', 'Component Name', 'Units', 'Scale',
                    'Offset','Attribute','Tags']
        self.setTable('components')
        #leftjoin so null values ok
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        #set the dropdowns
        #TODO column 2 also needs to trigger the name to be populated
        self.setRelation(2,QtSql.QSqlRelation('ref_component_type','code','code'))
        self.setRelation(7, QtSql.QSqlRelation('ref_attributes','code','code'))
        self.setRelation(4, QtSql.QSqlRelation('ref_power_units', 'code', 'code'))
        #database gets updated when fields are changed
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #select the data to display
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


