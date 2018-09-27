from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
import GBSUserInterface.ModelComponentTable as T
import GBSUserInterface.ModelEnvironmentTable as E
import GBSUserInterface.ModelFileInfoTable as F
import re
import os
import pytz
from GBSUserInterface.Delegates import ClickableLineEdit
from GBSUserInterface.gridLayoutSetup import setupGrid
from GBSController.UIToHandler import UIToHandler
from GBSUserInterface.makeButtonBlock import makeButtonBlock
from GBSUserInterface.TableHandler import TableHandler
from GBSUserInterface.ModelSetupInformation import SetupTag

from PyQt5 import QtWidgets,QtCore
# The file block is a group of widgets for entering file specific inputs
#its parent is FormSetup
class FileBlock(QtWidgets.QGroupBox):
    def __init__(self, parent, input):
        super().__init__(parent)
        #integer -> FileBlock
        self.init(input)

    # creates a single form for entering individual file type information
    def init(self, input):
        self.input = input
        windowLayout = self.createFileTab()
        self.setLayout(windowLayout)
        self.model = self.window().findChild(QtWidgets.QWidget,'setupDialog').model
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    # -> QVBoxLayout
    def createFileTab(self):
        self.dbhandler = ProjectSQLiteHandler()
        windowLayout = QtWidgets.QVBoxLayout()
        self.createTopBlock('Setup',self.assignFileBlock)
        l = self.FileBlock.findChild(QtWidgets.QWidget,'inputFileDirvalue')
        l.clicked.connect(self.lineclicked)
        windowLayout.addWidget(self.FileBlock)

        self.createTableBlock('Components', 'components', self.assignComponentBlock)

        windowLayout.addWidget(self.componentBlock)

        # the bottom block is disabled until a setup file is created or loaded
        self.createTableBlock('Environment Data', 'environment', self.assignEnvironmentBlock)

        windowLayout.addWidget(self.environmentBlock)
        return windowLayout

        # creates a horizontal layout containing gridlayouts for data input
    @QtCore.pyqtSlot()
    def lineclicked(self):
        '''opens a folder dialog and returns the string value of the pathway selected'''
        #if the directory has already been set then open the dialog to there otherwise default to current working directory
        curdir = self.findChild(QtWidgets.QWidget, 'inputFileDirvalue').text()
        if curdir == '':
            curdir = os.getcwd()
        folderDialog = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a directory.',curdir)
        if (folderDialog != ''):
            #once selected folderDialog gets set to the input box
            self.findChild(QtWidgets.QWidget, 'inputFileDirvalue').setText(folderDialog)
            #save the input to the setup data model and into the database
            self.saveInput()
            #update the filedir path
            if self.dbhandler.getInputPath(str(self.input)) is None:
                self.dbhandler.insertRecord('input_files',['inputfiledirvalue'],[folderDialog])
            else:
                self.dbhandler.updateRecord('input_files',['_id'],[str(self.input)],['inputfiledirvalue'],[folderDialog])
                print(self.dbhandler.dataCheck('input_files'))
            #filter the component and environemnt input tables to the current input directory
            self.filterTables()
            self.saveInput()
            self.model.writeNewXML()
        return folderDialog

    def createTopBlock(self,title, fn):
        '''The top block is where file information is set (format, date and time channels and file type)
        :param title: [String]
        :param fn: [method] used to assign the layout to a property'''

        # create a horizontal grouping to contain the top portion of the form
        gb = QtWidgets.QGroupBox(title)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setObjectName("setup")

        # add the setup grids
        g1 = {'headers': [1,2,3,4],
                  'rowNames': [1,2,3,4],
                  'columnWidths': [1, 1,1,3],
                  1:{1:{'widget':'lbl','name':'File Type:', 'default':'File Type'},
                     2:{'widget':'combo', 'name':'inputFileTypevalue', 'items':['csv', 'MET']},
                     3: {'widget': 'lbl', 'name': 'File Directory', 'default': 'Directory'},
                     4: {'widget': 'lncl', 'name': 'inputFileDirvalue'}
                     },
                  2: {1: {'widget': 'lbl', 'name': 'Date Channel','default':'Date Channel'},
                      2: {'widget': 'txt', 'name': 'dateChannelvalue'},
                      3: {'widget': 'lbl', 'name': 'Date Format','default':'Date Format'},
                      4: {'widget': 'combo', 'items': ['mm/dd/yy', 'mon-dd YYYY', 'mm/dd/YYYY','mm-dd-YYYY', 'dd/mm/YYYY'], 'name': 'dateChannelformat'}
                      },
                  3: {1: {'widget': 'lbl', 'name': 'Time Channel', 'default':'Time Channel'},
                      2: {'widget': 'txt', 'name': 'timeChannelvalue'},
                      3: {'widget': 'lbl', 'name': 'Time Format', 'default': 'Time Format'},
                      4: {'widget': 'combo', 'items': ['HH:MM:SS'], 'name': 'timeChannelformat'}
                      },
                  4:{1: {'widget': 'lbl', 'name': 'Time Zone', 'default':'Time Zone'},
                     2: {'widget': 'combo', 'items':pytz.all_timezones,'name': 'timeZonevalue','default':'America/Anchorage'},
                     3: {'widget': 'lbl', 'name': 'Use DST', 'default': 'Use DST'},
                     4: {'widget': 'chk', 'name': 'useDSTvalue', 'default':False}
                     }

                    }

        grid = setupGrid(g1)
        hlayout.addLayout(grid)
        hlayout.addStretch(1)
        gb.setLayout(hlayout)
        fn(gb)

    # layout for tables
    def createTableBlock(self, title, table, fn):

        gb = QtWidgets.QGroupBox(title)

        tableGroup = QtWidgets.QVBoxLayout()
        tableGroup.addWidget(self.dataButtons(table))
        if table == 'components':

            tv = T.ComponentTableView(self)
            tv.setObjectName('components')
            m = T.ComponentTableModel(self)


            tv.hideColumn(1)
            tv.setModel(m)
            tv.hideColumn(0)

            tableGroup.addWidget(tv, 1)
        else:
            tv = E.EnvironmentTableView(self)
            tv.setObjectName('environment')
            m = E.EnvironmentTableModel(self)

            tv.setModel(m)
            tv.hideColumn(0)
            tableGroup.addWidget(tv, 1)
        self.filterTables()
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        fn(gb)
        return

    # Load an existing descriptor file and populate the component table
    # -> None
    def functionForLoadDescriptor(self):

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
        handler = TableHandler(self)
        filedir = self.FileBlock.findChild(QtWidgets.QWidget, 'inputFileDirvalue').text()
        handler.functionForNewRecord(table,fields=[1],values=[filedir])


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
    def fillData(self, model,i):

        # dictionary of attributes of the class SetupTag belonging to a SetupInformation Model
        d = model.getSetupTags()
        # for every key in d find the corresponding textbox or combo box
        for k in d.keys():
            #values in d are setup tags and can contain list values
            #each key in the setuptag has its own display slot on the form
            #this fills the topblock
            tag_keys = d[k].keys()
            for t in tag_keys:
                if t != 'name':
                    edit_field = self.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox), k+t)

                    if type(edit_field) is QtWidgets.QLineEdit:
                        if len(d[k][t])>0:
                            edit_field.setText(d[k][t][self.input - 1])
                    elif type(edit_field) is ClickableLineEdit:
                        if len(d[k][t]) > 0:
                            edit_field.setText(d[k][t][self.input - 1])
                    elif type(edit_field) is QtWidgets.QComboBox:
                        if len(d[k][t]) > 0:
                            edit_field.setCurrentIndex(edit_field.findText(d[k][t][self.input - 1]))
        def getDefault(l, i):
            try:
                l[i]
                return l[i]
            except IndexError:
                return 'NA'

        # refresh the tables
        self.filterTables()

        return
    # Setters
    #(String, number, list or Object) ->
    def assignEnvironmentBlock(self, value):
        self.environmentBlock = value

    def assignComponentBlock(self,value):
        self.componentBlock = value

    def assignFileBlock(self,value):
        self.FileBlock = value
        self.FileBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.FileBlock.sizePolicy().retainSizeWhenHidden()
        self.FileBlock.setObjectName('fileInput')

    # if the fileblock looses focus update database information
    def focusOutEvent(self, event):

        if 'projectFolder' in self.model.__dict__.keys():
            #input to model
            self.saveInput()
            #input to database
            setupFields, setupValues = self.getSetupInfo()

            # update database table
            if not self.dbhandler.insertRecord('input_files', setupFields, setupValues):
                self.dbhandler.updateRecord('input_files', ['_id'], [str(setupValues[0])],
                                       setupFields[1:],
                                       setupValues[1:])
            # on leave save the xml files
            self.model.writeNewXML()
        return

    #reads data from an file input top block and returns a list of fields and values
    def getSetupInfo(self):
        fieldNames = ['_id']
        #values = [re.findall(r'\d+',self.input)[0]]
        values=[self.input]
        for child in self.FileBlock.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox)):

            if type(child) is QtWidgets.QLineEdit:
                fieldNames.append(child.objectName())
                values.append(child.text())
            elif type(child) is ClickableLineEdit:
                fieldNames.append(child.objectName())
                values.append(child.text())
            else:
                fieldNames.append(child.objectName())
                values.append(child.itemText(child.currentIndex()))

        return fieldNames,values

    #save the form input to the form setup data model
    def saveInput(self):

        #update model info from fileblock
        self.model.assignTimeChannel(SetupTag.assignValue, self.FileBlock.findChild(QtWidgets.QWidget, 'timeChannelvalue').text(),position=int(self.input)-1)
        self.model.assignTimeChannel(SetupTag.assignFormat, self.FileBlock.findChild(QtWidgets.QWidget, 'timeChannelformat').currentText(),position=int(self.input)-1)
        self.model.assignDateChannel(SetupTag.assignValue, self.FileBlock.findChild(QtWidgets.QWidget, 'dateChannelvalue').text(),position=int(self.input)-1)
        self.model.assignDateChannel(SetupTag.assignFormat, self.FileBlock.findChild(QtWidgets.QWidget, 'dateChannelformat').currentText(),position=int(self.input)-1)
        self.model.assignInputFileDir(SetupTag.assignValue, self.FileBlock.findChild(QtWidgets.QWidget,'inputFileDirvalue').text(),position=int(self.input)-1)
        self.model.assignInputFileType(SetupTag.assignValue, self.FileBlock.findChild(QtWidgets.QWidget,'inputFileTypevalue').currentText(),position=int(self.input)-1)
        self.model.assignTimeZone(SetupTag.assignValue,
                                       self.FileBlock.findChild(QtWidgets.QWidget, 'timeZonevalue').currentText(),
                                       position=int(self.input) - 1)
        self.model.assignUseDST(SetupTag.assignValue,
                                       str(self.FileBlock.findChild(QtWidgets.QWidget, 'useDSTvalue').isChecked()),
                                       position=int(self.input) - 1)

        self.saveTables()
        return

    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    def filterTables(self):
        tables = self.findChildren(QtWidgets.QTableView)
        filedir = self.FileBlock.findChild(QtWidgets.QWidget, 'inputFileDirvalue').text()
        self.filter = filedir
        for t in tables:
            m = t.model()
            m.setFilter("inputfiledir = '" + filedir + "'")
    def saveTables(self):
        '''get data from component and environment tables and update the setupInformation model
        components within a single directory are seperated with commas
        component info comes from the database not the tableview
        component names, units, scale, offset, attribute, fieldname get saved'''

        names = self.dbhandler.getComponentNames()
        names = list(set(names))
        self.model.assignComponentNames(SetupTag.assignValue, ' '.join(names))
        #df is a pandas dataframe  of component information
        df = self.dbhandler.getComponentsTable(self.filter)
        self.model.assignComponentName(SetupTag.assignValue,[','.join(df['component_name'].tolist())],position=int(self.input)-1)
        self.model.assignHeaderName(SetupTag.assignValue,[','.join(df['original_field_name'].tolist())],position=int(self.input)-1)
        self.model.assignComponentAttribute(SetupTag.assignValue,[','.join([x if x is not None else 'NA' for x in df['attribute'].tolist()])],position=int(self.input)-1)
        self.model.assignComponentAttribute(SetupTag.assignUnits,[','.join([x if x is not None else 'NA' for x in df['units'].tolist()])],position=int(self.input)-1)

    def close(self):
        if 'projectFolder' in self.model.__dict__.keys():
            #input to model
            self.saveInput()
            #input to database
            setupFields, setupValues = self.getSetupInfo()

            # update database table
            if not self.dbhandler.insertRecord('input_files', setupFields, setupValues):
                self.dbhandler.updateRecord('input_files', ['_id'], [setupFields[0]],
                                       setupFields[1:],
                                       setupValues[1:])
            self.saveTables()
            # on leave save the xml files
            self.model.writeNewXML()

        self.dbhandler.closeDatabase()