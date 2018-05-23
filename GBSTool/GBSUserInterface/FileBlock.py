from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
import GBSUserInterface.ModelComponentTable as T
import GBSUserInterface.ModelEnvironmentTable as E
import GBSUserInterface.ModelFileInfoTable as F
from GBSUserInterface.gridLayoutSetup import setupGrid
from GBSController.UIToHandler import UIToHandler
from GBSUserInterface.makeButtonBlock import makeButtonBlock
from GBSInputHandler.Component import Component
from PyQt5 import QtWidgets
# The file block is a group of widgets for entering file specific inputs
class FileBlock(QtWidgets.QGroupBox):
    def __init__(self, parent, input):
        super().__init__(parent)
        self.init(input)

    # creates a single form for entering individual file type information
    def init(self, input):
        self.input = input
        windowLayout = self.createFileTab()
        self.setLayout(windowLayout)

    # -> QVBoxLayout
    def createFileTab(self):
        windowLayout = QtWidgets.QVBoxLayout()
        self.createTableBlock('Setup', 'inputFile',self.assignFileBlock)
        # the topBlock is hidden until we load or create a setup xml
        #self.FileBlock.setEnabled(False)
        windowLayout.addWidget(self.FileBlock)

        self.createTableBlock('Components', 'components', self.assignComponentBlock)
        #self.componentBlock.setEnabled(False)
        windowLayout.addWidget(self.componentBlock)

        # the bottom block is disabled until a setup file is created or loaded
        self.createTableBlock('Environment Data', 'environment', self.assignEnvironmentBlock)
        #self.environmentBlock.setEnabled(False)
        windowLayout.addWidget(self.environmentBlock)
        return windowLayout

        # creates a horizontal layout containing gridlayouts for data input
        # TODO this changes to a table view.
    # def createTopBlock(self):
    #     # create a horizontal grouping to contain the top setup xml portion of the form
    #     self.topBlock = QtWidgets.QGroupBox('Setup XML')
    #     hlayout = QtWidgets.QHBoxLayout()
    #
    #     hlayout.setObjectName("layout1")
    #
    #     # add the setup grids
    #     g1 = {'headers': ['Attribute', 'Field', 'Format'],
    #               'rowNames': ['Date', 'Time', 'Load'],
    #               'columnWidths': [1, 1, 1],
    #               'Date': {'Field': {'widget': 'txt', 'name': 'dateChannelvalue'},
    #                        'Format': {'widget': 'combo', 'items': ['ordinal'], 'name': 'dateChannelformat'},
    #                        },
    #               'Time': {'Field': {'widget': 'txt', 'name': 'timeChannelvalue'},
    #                        'Format': {'widget': 'combo', 'items': ['excel'], 'name': 'timeChannelformat'}
    #                        }
    #               }
    #     grid = setupGrid(g1)
    #     hlayout.addLayout(grid)
    #     hlayout.addStretch(1)
    #     # add the second grid
    #     g2 = {'headers': ['TimeStep', 'Value', 'Units'],
    #               'rowNames': ['Input', 'Output'],
    #               'columnWidths': [1, 1, 1],
    #               'Input': {'Value': {'widget': 'txt', 'name': 'inputTimeStepvalue'},
    #                         'Units': {'widget': 'combo', 'items': ['S', 'M', 'H'], 'name': 'inputTimeStepunit'}
    #                         },
    #               'Output': {'Value': {'widget': 'txt', 'name': 'timeStepvalue'},
    #                          'Units': {'widget': 'combo', 'items': ['S', 'M', 'H'], 'name': 'timeStepunit'}}
    #               }
    #     grid = setupGrid(g2)
    #     hlayout.addLayout(grid)
    #
    #     # add another stretch to keep the grids away from the right edge
    #     hlayout.addStretch(1)
    #     self.topBlock.setObjectName('format')
    #     self.topBlock.setLayout(hlayout)
    #     self.topBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #     self.topBlock.sizePolicy().retainSizeWhenHidden()

        # layout for tables
    def createTableBlock(self, title, table, fn):

        gb = QtWidgets.QGroupBox(title)

        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons(table))
        if table == 'components':
            tv = T.ComponentTableView(self)
            tv.setObjectName('components')
            m = T.ComponentTableModel(self)
        elif table == 'inputFile':
            tv = F.FileInfoTableView(self)
            tv.setObjectName('inputFile')
            m = F.FileInfoTableModel(self)

        else:
            tv = E.EnvironmentTableView(self)
            tv.setObjectName('environment')
            m = E.EnvironmentTableModel(self)

        tv.setModel(m)

        tv.hideColumn(0)

        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        fn(gb)
        return

    # Load an existing descriptor file and populate the component table
    # -> None
    def functionForLoadDescriptor(self):
        # TODO temporary message to prevent unique index error
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Load Descriptor',
                                    'If the component descriptor file you are loading has the same name as an existing component it will not load')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

        tableView = self.findChild((QtWidgets.QTableView), 'components')
        model = tableView.model()
        # identify the xml
        descriptorFile = QtWidgets.QFileDialog.getOpenFileName(self, "Select a descriptor file", None, "*xml")
        if (descriptorFile == ('', '')) | (descriptorFile is None):
            return

        fieldName, ok = QtWidgets.QInputDialog.getText(self, 'Field Name',
                                                       'Enter the name of the channel that contains data for this component.')
        # if a field was entered add it to the table model and database
        if ok:
            record = model.record()
            record.setValue('original_field_name', fieldName)

            handler = UIToHandler()
            record = handler.copyDescriptor(descriptorFile[0], self.model.componentFolder, record)

            # add a row into the database
            model.insertRowIntoTable(record)
            # refresh the table
            model.select()
        return

    # Add an empty record to the specified datatable
    # String -> None
    def functionForNewRecord(self, table):
        # add an empty record to the table

        # get the model
        tableView = self.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        # insert an empty row as the last record

        model.insertRows(model.rowCount(), 1)

        model.submitAll()

    # delete the selected record from the specified datatable
    # String -> None
    def functionForDeleteRecord(self, table):

        # get selected rows
        tableView = self.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        # selected is the indices of the selected rows
        selected = tableView.selectionModel().selection().indexes()
        if len(selected) == 0:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Select Rows',
                                        'Select rows before attempting to delete')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Confirm Delete',
                                        'Are you sure you want to delete the selected records?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            result = msg.exec()

            if result == QtWidgets.QMessageBox.Ok:
                handler = UIToHandler()
                removedRows = []
                for r in selected:
                    if r.row() not in removedRows:
                        if table == 'components':
                            # remove the xml files too
                            handler.removeDescriptor(model.data(model.index(r.row(), 3)),
                                                     self.model.componentFolder)
                        removedRows.append(r.row())
                        model.removeRows(r.row(), 1)

                # Delete the record from the database and refresh the tableview
                model.submitAll()
                model.select()

    # string -> QGroupbox
    def dataButtons(self, table):
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()

        if table == 'components':
            buttonRow.addWidget(makeButtonBlock(self, self.functionForLoadDescriptor,
                                                None, 'SP_DialogOpenButton',
                                                'Load a previously created component xml file.'))

        buttonRow.addWidget(makeButtonBlock(self, lambda: self.functionForNewRecord(table),
                                            '+', None,
                                            'Add a component'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: self.functionForDeleteRecord(table),
                                            None, 'SP_TrashIcon',
                                            'Delete a component'))
        buttonRow.addStretch(3)
        buttonBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        buttonBox.setLayout(buttonRow)
        return buttonBox

    # TODO this needs to change if its populating from a table
    # inserts data from the data model into corresponding boxes on the screen
    # SetupInfo -> None
    def fillData(self, model):

        # dictionary of attributes of the class SetupTag belonging to a SetupInformation Model
        d = model.getSetupTags()

        # for every key in d find the corresponding textbox or combo box

        for k in d.keys():

            for a in d[k]:
                if d[k][a] is not None:
                    edit_field = self.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox), k + a)

                    if type(edit_field) is QtWidgets.QLineEdit:

                        edit_field.setText(d[k][a])
                    elif type(edit_field) is QtWidgets.QComboBox:
                        edit_field.setCurrentIndex(edit_field.findText(d[k][a]))

        def getDefault(l, i):
            try:
                l[i]
                return l[i]
            except IndexError:
                return 'NA'

        # this is what happens if there isn't already a project database.
        if not self.projectDatabase:

            # for headers, componentnames, componentattributes data goes into the database for table models
            dbHandler = ProjectSQLiteHandler()
            # for every field listed in the header name tag create a table entry on the form
            for i in range(len(model.headerName.value)):

                fields = ('original_field_name', 'component_name', 'attribute', 'units')
                # as long as an NA isn't returned for the field name get the values for that field
                if (getDefault(model.headerName.value, i) != 'NA'):
                    values = (getDefault(model.headerName.value, i), getDefault(model.componentName.value, i),
                              getDefault(model.componentAttribute.value, i),
                              getDefault(model.componentAttribute.unit, i))

                    # if the attribute is in the environment list then the data gets placed in the environment table
                    if getDefault(model.componentAttribute.value, i) in ['WS', 'WF', 'IR', 'Tamb', 'Tstorage']:
                        # insert into environment table
                        table = 'environment'
                    else:
                        table = 'components'
                        # if its the components table then we need to fill in component type as well
                        fields = fields + ('component_type',)
                        componentType = getDefault(model.componentName.value, i)[0:3]
                        values = values + (componentType,)

                    if len(dbHandler.cursor.execute(
                            "select * from " + table + " WHERE component_name = '" + getDefault(
                                model.componentName.value, i) + "'").fetchall()) < 1:
                        dbHandler.insertRecord(table, fields, values)
            dbHandler.closeDatabase()

        # refresh the tables
        tableView = self.findChild((QtWidgets.QTableView), 'environment')
        tableModel = tableView.model()
        tableModel.select()
        tableView = self.findChild((QtWidgets.QTableView), 'components')
        tableModel = tableView.model()
        tableModel.select()
        return
    # Setters
    #(String, number, list or Object) ->
    def assignEnvironmentBlock(self, value):
        self.environmentBlock = value

    def assignComponentBlock(self,value):
        self.componentBlock = value
    def assignFileBlock(self,value):
        self.FileBlock = value