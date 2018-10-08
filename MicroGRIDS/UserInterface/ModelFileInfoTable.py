
from GBSUserInterface.Delegates import *
#subclass of QTableView for displaying inputFile information
class FileInfoTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #set text boxes
        t_boxes =[3,4,5,7]
        for i in t_boxes:
            self.setItemDelegateForColumn(i, TextDelegate(self))
        self.setColumnHidden(0, True)
        #set combo boxes
        combos = [1,2,6,8]
        for c in combos:
            self.setItemDelegateForColumn(c,RelationDelegate(self,None))

#Tabel model to be displayed in InputFile tableview
class FileInfoTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self,parent):
        QtSql.QSqlRelationalTableModel.__init__(self, parent)
        self.header = ['ID','File Type','Data Type','Directory','Time Sample Interval',
                   'Date Channel','Date Format','Time Channel','Time Format','Channels']


        self.setTable('inputFiles')
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.setRelation(1, QtSql.QSqlRelation('ref_file_type', 'code', 'code'))
        self.setRelation(2, QtSql.QSqlRelation('ref_data_format', 'code', 'code'))
        self.setRelation(6, QtSql.QSqlRelation('ref_date_format', 'code', 'code'))
        self.setRelation(8, QtSql.QSqlRelation('ref_time_format', 'code', 'code'))
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

