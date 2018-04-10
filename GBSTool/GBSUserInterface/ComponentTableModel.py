from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from ComponentSQLiteHandler import SQLiteHandler
from Delegates import *

#subclass of QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
       #TODO delegate positions need to be changed and delete, add and upload buttons need to be put above table.
        #myHandler = SQLiteHandler('component_manager')
        #attributes are column 8
        # self.attributes = ComboReference('component_attributes',['ref_attributes'],myHandler)
        #self.setItemDelegateForColumn(6, ComboDelegate(self,self.attributes.values))
        #types are column 3
        #self.component_type = ComboReference('component_type',['ref_component_type'],myHandler)
        #self.setItemDelegateForColumn(2,ComboDelegate(self,self.component_type.values))
        # self.units = ComboReference('load_units',['ref_load_units'],myHandler)
        # self.tf = ComboReference('isVoltage',['ref_true_false'],myHandler)
        #self.setItemDelegateForColumn(10, ComboDelegate(self, self.tf.values))

        #self.setItemDelegateForColumn(4, ComboDelegate(self, self.units.values))
        #button to navigate to descriptor xml file is in column 0
        #self.setItemDelegateForColumn(1,ButtonDelegate(self, 'SP_DialogOpenButton'))
        #button to delete a component is in column 2
        #self.setItemDelegateForColumn(2, ButtonDelegate(self, 'SP_TrashIcon'))

        t_boxes = [1,2,4,5,7,8,9]
        #columns to hide
        hidden = 0

        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        self.setColumnHidden(0, True)
        self.setItemDelegateForColumn(2,QtSql.QSqlRelationalDelegate(self))
        #combos is the list of components that are associated with combo boxes
        #self.combos = [x for x in self.__dict__.keys() if type(self.__getattribute__(x)) == ComboReference]
        #myHandler.closeDatabase()

class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):
        QtSql.QSqlTableModel.__init__(self, parent)
        self.header = ['ID','Field', 'Type', 'Component Name', 'Units', 'Scale',
                    'Offset','Attribute','P in max pa','Q in max pa','Q out max pa','Voltage Source','Tags']

        self.setTable('components')
        self.setRelation(2,QtSql.QSqlRelation('ref_component_type','code','code'))

        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()
