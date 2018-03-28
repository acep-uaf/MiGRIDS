import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore

from ComponentSQLiteHandler import SQLiteHandler
from SetupInformation import SetupInformation



class SetupWizard:
    global model
    model = SetupInformation()
    #dialog sequence is a WizardTree containing info to be used when making dialog widgets
    def __init__(self, dialogSequence):
        self.dialogSequence = dialogSequence
        #Starts with the parent node for the entire sequence of dialogs
        self.currentDialog = dialogSequence.getStart()
        self.makeDialog(self.currentDialog)
        self.input = None
    #connect to the sqlite database containing reference tables
    def connect(self):
        self.database = SQLiteHandler('component_manager')

    #dissconnect from the sqlite database containing reference tables
    def disconnect(self):
        self.database.closeDatabase()

    #advances the wizard to the next dialog frame
    def nextDialog(self):
        global model
        # if we are at the last dialog then the positive button becomes a done button
        if type(self.inputWidget) is QtWidgets.QComboBox:
            self.input = self.parseCombo(self.inputWidget.currentText())
        elif type(self.inputWidget) is QtWidgets.QGroupBox:
            #get the value from the text box
            self.input = self.inputWidget.findChild(QtWidgets.QLineEdit,'folder').text()
        else:
            self.input = self.inputWidget.text()
        model.assign(self.currentDialogWindow.objectName(), self.input)
        self.currentDialogWindow.close()
        #get the next dialog from the wizardtree
        d = self.dialogSequence.getNext(self.currentDialog.key)
        self.makeDialog(d)

    #returns to the previous dialog frame
    def previousDialog(self):
        #TODO get the input value and write it to the data model
        self.currentDialogWindow.close()
        d = self.dialogSequence.getPrevious(self.currentDialog.key)
        self.makeDialog(d)

    #create an input widget to display on the dialog
    #widget, string -> None
    def createInput(self, reftable, folderDialog = False):
        self.connect()
        if folderDialog:
            self.inputWidget = self.makeFolderSelectorInput()
        elif reftable is not None:
            #create a combo box
            values = pd.read_sql_query("select code, description from " + reftable, self.database.connection)

            valueStrings = []
            for v in range(len(values)):

                valueStrings.append(values.loc[v,'code']+ ' - ' + values.loc[v,'description'])
            self.inputWidget = self.makeComboInput(valueStrings)
        else:
            #create an input box
            self.inputWidget = self.makeTextInput()
        self.disconnect()

    #makes a dialog box containing relevant information specified by the WizardTree
    #WizardTree -> None
    def makeDialog(self,dialog):
        d = dialog.value

        self.currentDialog = dialog
        self.currentDialogWindow = QtWidgets.QDialog()
        self.currentDialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.currentDialogWindow.setWindowTitle(d['title'])
        self.currentDialogWindow.setObjectName(d['title'])
        vl = QtWidgets.QVBoxLayout()
        p =QtWidgets.QLabel(d['prompt'],self.currentDialogWindow)
        vl.addWidget(p)
        vl.addStretch(2)

        #input layout
        #if a reference table is provided create a combobox otherwise its a text input box
        #assumes code and description column from ref table will be displayed, code will be the submitted value
        self.createInput(d['reftable'], d['folder'])
        vl.addWidget(self.inputWidget)

        #button layout
        hl = QtWidgets.QHBoxLayout()
        posButton = self.posButton()
        negButton = self.negButton()

        hl.addWidget(posButton)
        hl.addStretch(2)
        hl.addWidget(negButton)
        vl.addLayout(hl)

        self.currentDialogWindow.setLayout(vl)
        self.currentDialogWindow.exec()
    #String -> String
    def parseCombo(self,inputString):
        s = inputString.split(" - ")[0]
        return s
    def posButton(self):

        #otherwise it is the ok button
        if self.currentDialog.isLast():
            b = QtWidgets.QPushButton('done', self.currentDialogWindow)
            b.clicked.connect(self.wizardComplete)
        else:
            b = QtWidgets.QPushButton('next', self.currentDialogWindow)
            b.clicked.connect(self.nextDialog)
        #TODO save responses to SetupInformation
        return b

    def negButton(self):
        # if we are at the first dialog then the positive button becomes a cancel button
        # otherwise it is the previous button
        if self.currentDialog.isStart():
            b = QtWidgets.QPushButton('cancel', self.currentDialogWindow)
            b.clicked.connect(self.wizardComplete)
        else:

            b = QtWidgets.QPushButton('previous', self.currentDialogWindow)
            b.clicked.connect(self.previousDialog)
        #TODO save responses
        return b

    def makeTextInput(self):
        txt = QtWidgets.QLineEdit()
        txt.inputMethodHints()
        return txt

    def makeFolderSelectorInput(self):
        ButtonBlock = QtWidgets.QGroupBox()
        layout = QtWidgets.QHBoxLayout()
        txt = QtWidgets.QLineEdit()
        txt.setObjectName('folder')

        layout.addWidget(txt)
        btn = QtWidgets.QPushButton()
        btn.setIcon(btn.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogOpenButton')))
        btn.clicked.connect(lambda: self.launchFinder(ButtonBlock))
        layout.addWidget(btn)

        ButtonBlock.setLayout(layout)
        return ButtonBlock

    def makeComboInput(self, values):
        cmb = QtWidgets.QComboBox()
        cmb.addItems(values)
        return cmb
    #finder is a directory search dialog that returns information to its parent dialog.
    def launchFinder(self, parent):
        import os
        folderDialog = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a directory.',os.getcwd())
        #once selected folderDialog gets set to the input box
        textBlock = parent.findChild(QtWidgets.QLineEdit, 'folder')
        textBlock.setText(folderDialog)
        return dir

    def wizardComplete(self):
        self.currentDialogWindow.close()
        #TODO
        #write the setup information to an xml
        global model
        model.writeXML()
        #display the information in the UISetupForm
