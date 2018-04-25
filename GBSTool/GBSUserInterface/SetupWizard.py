#class to navigate through the user setup wizard tree
#responses get recorded in the ModelSetupInformation class and written to xml in the project folder

import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore

from ProjectSQLiteHandler import ProjectSQLiteHandler

class SetupWizard:

    #dialog sequence is a WizardTree containing info to be used when making dialog widgets
    def __init__(self, dialogSequence, model,parentWindow):

        self.dialogSequence = dialogSequence
        #Starts with the parent node for the entire sequence of dialogs
        self.currentDialog = dialogSequence.getStart()
        self.model = model
        self.makeDialog(self.currentDialog)
        self.input = None
        self.parentWindow = parentWindow


    #connect to the sqlite database containing reference tables
    def connect(self):

        self.database = ProjectSQLiteHandler('project_manager')

    #dissconnect from the sqlite database containing reference tables
    def disconnect(self):
        self.database.closeDatabase()

    #advances the wizard to the next dialog window
    def nextDialog(self):
        response = self.recordValue()
        self.currentDialogWindow.close()
        #get the next dialog from the wizardtree

        d = self.dialogSequence.getNext(self.currentDialog.key, response)

        self.makeDialog(d)

    #returns the response from a dialog input
    #->string
    def recordValue(self):


        response = 0
        if type(self.inputWidget) is QtWidgets.QComboBox:
            self.input = self.parseCombo(self.inputWidget.currentText())
            response = self.inputWidget.currentIndex()

        elif type(self.inputWidget) is QtWidgets.QGroupBox:
            # get the value from the text box
            self.input = self.inputWidget.findChild(QtWidgets.QLineEdit, 'folder').text()
        else:
            self.input = self.inputWidget.text()
        self.model.assign(self.currentDialogWindow.objectName(), self.input)
        return response
    #returns to the previous dialog frame
    #data in the current dialog does not get written to the model
    def previousDialog(self):
        self.currentDialogWindow.close()
        d = self.dialogSequence.getPrevious(self.currentDialog.key)
        self.makeDialog(d)

    #create an input widget to display on the dialog
    #widget, string -> None
    def createInput(self, reftable, folderDialog = False):

        if folderDialog:
            self.inputWidget = self.makeFolderSelectorInput()
        elif reftable is not None:
            self.connect()
            #create a combo box
            values = pd.read_sql_query("select code, description from " + reftable, self.database.connection)
            self.disconnect()
            valueStrings = []
            for v in range(len(values)):

                valueStrings.append(values.loc[v,'code']+ ' - ' + values.loc[v,'description'])
            self.inputWidget = self.makeComboInput(valueStrings)
        else:
            #create an input box
            self.inputWidget = self.makeTextInput()


    #makes a dialog box containing relevant information specified by the WizardTree
    #WizardTree -> None
    def makeDialog(self,dialog):
        d = dialog.value

        self.currentDialog = dialog
        self.currentDialogWindow = QtWidgets.QDialog()
        self.currentDialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.currentDialogWindow.setWindowTitle(d['title'])
        self.currentDialogWindow.setObjectName(d['name'])
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

        hl.addWidget(negButton)
        hl.addStretch(2)
        hl.addWidget(posButton)
        vl.addLayout(hl)

        self.currentDialogWindow.setLayout(vl)
        self.currentDialogWindow.exec()

    #String -> String
    #parses a string - string formatted item into its first string component (code)
    def parseCombo(self,inputString):
        s = inputString.split(" - ")[0]
        return s

    #create a button to reside in the positive response position.
    #if its the last dialog then it calls the WizardComplete function with the finished argument = True
    #otherwise it calls the nextDialog function
    #->QPushButton
    def posButton(self):
        #otherwise it is the ok button
        if self.dialogSequence.getNext(self.currentDialog.key) is None:
            b = QtWidgets.QPushButton('done', self.currentDialogWindow)
            b.clicked.connect(lambda: self.wizardComplete(True))
        else:
            b = QtWidgets.QPushButton('next', self.currentDialogWindow)
            b.clicked.connect(self.nextDialog)

        return b
    #->QPushButton
    #creates a negative button
    #if the current dialog window is the last window the button will initiate the wizardComplete function
    #otherwise it will initiate the next dialog window
    def negButton(self):
        # if we are at the first dialog then the positive button becomes a cancel button
        # otherwise it is the previous button
        if self.currentDialog.isStart():
            b = QtWidgets.QPushButton('cancel', self.currentDialogWindow)
            b.clicked.connect(self.wizardComplete)
        else:

            b = QtWidgets.QPushButton('previous', self.currentDialogWindow)
            b.clicked.connect(self.previousDialog)
        return b

    #creates a text box input widget
    def makeTextInput(self):
        txt = QtWidgets.QLineEdit()
        txt.inputMethodHints()
        return txt

    #None->QGroupBox
    #creates the QGroupBox containing a text input and button that launches the folder finder dialog
    #folder finder dialog results are returned to the text box in the parent dialog
    def makeFolderSelectorInput(self):
        inputBlock = QtWidgets.QGroupBox()
        layout = QtWidgets.QHBoxLayout()
        txt = QtWidgets.QLineEdit()
        txt.setObjectName('folder')

        layout.addWidget(txt)
        btn = QtWidgets.QPushButton()
        btn.setIcon(btn.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogOpenButton')))
        btn.clicked.connect(lambda: self.launchFinder(inputBlock))
        layout.addWidget(btn)

        inputBlock.setLayout(layout)
        return inputBlock

    #creates a combo box with specified items
    #listOfStrings ->QComboBox
    def makeComboInput(self, values):
        cmb = QtWidgets.QComboBox()
        cmb.addItems(values)
        return cmb

    #finder is a directory search dialog that returns a path string to its parent dialog.
    #Widget -> String
    def launchFinder(self, parent):
        import os
        folderDialog = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a directory.',os.getcwd())
        #once selected folderDialog gets set to the input box
        textBlock = parent.findChild(QtWidgets.QLineEdit, 'folder')
        textBlock.setText(folderDialog)
        return dir

    #Boolean ->
    #closes the dialog wizard and writes the results to the project folder if the setup process was completed
    def wizardComplete(self, finished = False):
        self.currentDialogWindow.close()
        self.recordValue()
        if finished:
            self.model.writeNewXML()

