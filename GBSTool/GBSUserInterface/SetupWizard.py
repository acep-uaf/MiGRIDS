import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore

from ComponentSQLiteHandler import SQLiteHandler
class SetupWizard:
    #dialog sequence is a WizardTree containing info to be used when making dialog inputs
    def __init__(self, dialogSequence):
        self.dialogSequence = dialogSequence
        #currentDialog the current node. It starts with the parent node for the entire sequence
        self.currentDialog = dialogSequence.getStart()
        self.makeDialog(self.currentDialog)
        self.connect()

    def connect(self):
        self.database = SQLiteHandler('component_manager')
    def disconnect(self):
        self.database.closeDatabase()
    #advances the wizard to the next dialog frame
    def nextDialog(self):
        self.currentDialogWindow.close()
        #get the next dialog from the wizardtree
        d = self.dialogSequence.getNext(self.currentDialog.key)
        self.makeDialog(d)



    #returns to the previous dialog frame
    def previousDialog(self):
        self.currentDialogWindow.close()
        d = self.dialogSequence.getPrevious(self.currentDialog.key)
        self.makeDialog(d)

    #p is parent widget
    #widget, string -> widget
    def createInput(self, reftable):
        self.connect()
        if reftable is not None:
            #create a combo box
            values = pd.read_sql_query("select code, description from " + reftable, self.database.connection)

            valueStrings = []
            for v in range(len(values)):

                valueStrings.append(values.loc[v,'code']+ ' - ' + values.loc[v,'description'])
            i = self.makeComboInput(valueStrings)
        else:
            #create an input box
            i = self.makeTextInput()
        self.disconnect()
        return i
    #makes a dialog box containing relevant information
    def makeDialog(self,dialog):
        d = dialog.value
        print(d)
        self.currentDialog = dialog
        self.currentDialogWindow = QtWidgets.QDialog()
        self.currentDialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.currentDialogWindow.setWindowTitle(d['title'])
        vl = QtWidgets.QVBoxLayout()
        p =QtWidgets.QLabel(d['prompt'],self.currentDialogWindow)
        vl.addWidget(p)
        vl.addStretch(2)
        #input layout
        #if a reference table is provided use a combobox
        #assumes code and description column from ref table will be displayed, code will be stored
        inputWidget = self.createInput(d['reftable'])
        vl.addWidget(inputWidget)
        #otherwise input textbox
        #button layout
        hl = QtWidgets.QHBoxLayout()
        posButton = self.posButton()
        negButton = self.negButton()

        hl.addWidget(posButton)
        hl.addStretch(2)
        hl.addWidget(negButton)
        vl.addLayout(hl)

        #
        self.currentDialogWindow.setLayout(vl)
        self.currentDialogWindow.exec()

    def posButton(self):
        #if we are at the last dialog then the positive button becomes a done button
        #otherwise it is the ok button
        if self.currentDialog.isLast():
            b = QtWidgets.QPushButton('Done', self.currentDialogWindow)
            b.clicked.connect(self.wizardComplete)
        else:
            b = QtWidgets.QPushButton('next', self.currentDialogWindow)
            b.clicked.connect(self.nextDialog)
        #TODO save responses
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

    def makeComboInput(self, values):
        cmb = QtWidgets.QComboBox()
        cmb.addItems(values)
        return cmb

    def wizardComplete(self):
        self.currentDialogWindow.close()
