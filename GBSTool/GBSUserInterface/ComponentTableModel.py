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
        myHandler = SQLiteHandler('component_manager')
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
        myHandler.closeDatabase()

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

# #Tabel model to be displayed in component tableview
# class ComponentTableModel(QtCore.QAbstractTableModel):
#     def __init__(self,parent):
#         QtCore.QAbstractTableModel.__init__(self, parent)
#         self.db = SQLiteHandler("component_manager")
#
#         self.header,self.columns = self.getHeader(self.db)
#
#     #QModelIndex -> integer
#     #returns the number of rows to display
#     #number of rows equals the number of components + an empty row
#     def rowCount(self, parent = QtCore.QModelIndex()):
#
#         return self.db.getComponentTableCount() + 1
#
#     # QModelIndex -> integer
#     #returns the number of columns to display
#     def columnCount(self, parent = QtCore.QModelIndex()):
#         return len(self.columns)
#
#     # index, Qt.DisplayRole -> String
#     def data(self, index, role=QtCore.Qt.DisplayRole):
#         if not index.isValid:
#             return None
#         if not role==QtCore.Qt.DisplayRole:
#             return None
#
#         v = self.db.getComponentData(self.columns[index.column()],index.row())
#         if v is None:
#             v = ''
#         #if its feeding a combo box get the list position
#         if self.db.hasRef(self.columns[index.column()]):
#             rvalues = self.db.getCodes(self.db.getRef(self.columns[index.column()]))
#
#             #select the matching combo
#
#             v = [i for i,x in enumerate(rvalues) if x == v]
#             #TODO change this so code list includes empty first position then we don't need to add 1 and position will be correct for coombined reference tables
#             # add 1 to account for empty first position in combo boxes
#             if len(v)>0:
#                 v = v[0] +1
#             else:
#                 v = 0
#
#
#
#         return v
#
#     #SQLitedatbase connection -> listOfStrings
#     def getHeader(self,db):
#
#
#
#         headers = ['Field',' ',' ','Type','Component Name','Units','Scale',
#                    'Offset','Attribute','P in max pa','Q in max pa','Q out max pa','Voltage Source','Tags']
#         columnNames = ['original_field_name','','','component_type', 'component_name', 'units', 'scale',
#                        'offset', 'attribute', 'p_in_maxpa', 'q_in_maxpa', 'q_out_maxpa', 'is_voltage_source', 'tags']
#         return headers, columnNames
#     #index -> string
#     def makeComponentName(self,index):
#         import os
#         #get the component type
#
#         componentType = self.data(self.index(index.row(), 3))
#         print('component type: %s' %componentType)
#         #count the number of existing components with that type
#         e = self.db.getComponentTableCount()
#         e = e+1
#         return componentType + e
#
#     def headerData(self, section: int, orientation, role):
#         if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
#             return QtCore.QVariant(self.header[section])
#         return QtCore.QVariant()
#
#     #index, string, DisplayRole -> string
#     def setData(self, index, value, role=QtCore.Qt.DisplayRole):
#         from UIToHandler import UIToHandler
#         from Component import Component
#         import os
#         #columns 0, 3 and 4 are required to write any data to database or xml
#
#         if index.column() in [0,3]:
#             check1 = self.data(self.index(index.row(), 0))
#             check2 = self.data(self.index(index.row(), 3))
#             print('check1 is %s' %check1)
#             print(check2)
#             if self.missingData(check1) | self.missingData(check2):
#                 print('required data is missing')
#                 #Don't do anything if required data is still missing
#                 return
#             else:
#
#                 #if no name has been created yet then create it
#                 if self.data(self.index(index.row(), 4)) == '':
#                     typecount = self.db.getTypeCount(self.data(self.index(index.row(), 3)))
#                     self.makeComponentName(index, typecount+1)
#
#                 componentFolder = os.path.join(self.parent().model.setupFolder, '../Components')
#                 #componentFolder = '../Components'
#                 print(componentFolder)
#                 component = Component(component_name=self.data(self.index(index.row(), 4)),
#                                      units=self.data(self.index(index.row(), 5)),
#                                      scale=self.data(self.index(index.row(), 6)),
#                                      offset=self.data(self.index(index.row(), 7)),
#                                      attribute=self.data(self.index(index.row(), 8)),
#                                      type=self.data(self.index(index.row(), 3)),
#                                      pinmaxpa= self.data(self.index(index.row(), 9)),
#                                      qinmaxpa=self.data(self.index(index.row(), 10)),
#                                      qoutmaxpa=self.data(self.index(index.row(), 11)),
#                                      voltagesource=self.data(self.index(index.row(), 12)),
#                                      tags={},
#                                       filepath=componentFolder)
#                 # find the table parameter that changed so we don't overwrite the entire file in case manual edits were made
#                 tag = self.columns[index.column()]
#                 # component information is stored in the project sqlite database then written to xml
#                 print(component.toDictionary())
#                 isNew = self.db.writeComponent(component.toDictionary()[component.component_name])
#                 #self.db.closeDatabase()
#
#                 #write the xml
#                 handler = UIToHandler()
#                 if isNew:
#                     handler.makeComponentDescriptor(component.toDictionary()[component.component_name])
#                     #values also need to be written to the setup xml
#                     #original_header_list
#                     #component_name_list
#                     print(self.parent())
#                     print(self.parent().parent())
#                 else:
#                     if(tag in component.toDictionary()[component.component_name].keys()):
#                         handler.fillComponentDiscriptor(component.toDictionary()[component.component_name],tag)
#
#
#                 print("setData", index.row(), index.column(), value)
#
#
#         return str(value)
#
#     def missingData(self,value):
#         print(value)
#         print(value)
#         #if a combobox is set to 0 or a text field is an empty string then the data is missing
#         if (value == 0) | (value == ''):
#                 return True
#         return False
#
#     #index -> Boolean
#     def flags(self, index):
#         # if (index.column() == 0):
#         #     return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
#         # else:
#         #     return QtCore.Qt.ItemIsEnabled
#         return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled