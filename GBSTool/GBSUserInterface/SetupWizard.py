from PyQt5 import QtWidgets, QtGui, QtCore

class SetupWizard:
    #dialog sequence is a WizardTree containing info to be used when making dialog inputs
    def __init__(self, dialogSequence):
        self.dialogSequence = dialogSequence
        #currentDialog the current node. It starts with the parent node for the entire sequence
        self.currentDialog = dialogSequence.getStart()
        self.makeDialog(self.currentDialog)

    #advances the wizard to the next dialog frame
    def nextDialog(self):
        self.currentDialogWindow.close()
        #get the next dialog from the wizardtree
        print(self.currentDialog.key)
        d = self.dialogSequence.getNext(self.currentDialog.key)
        print(d.key)
        self.makeDialog(d)
        print('next')
        #return n
    #returns to the previous dialog frame
    def previousDialog(self):
        self.currentDialogWindow.close()
        d = self.dialogSequence.getPrevious(self.currentDialog.key)
        self.makeDialog(d)
        print('previous')
        #return p

    #makes a dialog box containing relevant information
    def makeDialog(self,dialog):
        d = dialog.value
        self.currentDialog = dialog
        self.currentDialogWindow = QtWidgets.QDialog()
        self.currentDialogWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.currentDialogWindow.setWindowTitle(d['title'])
        vl = QtWidgets.QVBoxLayout()
        p =QtWidgets.QLabel(d['prompt'],self.currentDialogWindow)
        vl.addWidget(p)
        vl.addStretch(2)
        hl = QtWidgets.QHBoxLayout()

        posButton = self.posButton()
        negButton = self.negButton()

        hl.addWidget(posButton)
        hl.addStretch(2)
        hl.addWidget(negButton)
        vl.addLayout(hl)
        self.currentDialogWindow.setLayout(vl)
        self.currentDialogWindow.exec()

    def posButton(self):
        #if we are at the last dialog then the positive button becomes a done button
        #otherwise it is the ok button
        if self.dialogSequence.isLast():
            b = QtWidgets.QPushButton('Done', self.currentDialogWindow)
            b.clicked.connect(self.wizardComplete)
        else:
            b = QtWidgets.QPushButton('next', self.currentDialogWindow)
            b.clicked.connect(self.nextDialog)

        return b

    def negButton(self):
        # if we are at the first dialog then the positive button becomes a cancel button
        # otherwise it is the previous button
        if self.dialogSequence.isStart():
            b = QtWidgets.QPushButton('cancel', self.currentDialogWindow)
            b.clicked.connect(self.wizardComplete)
        else:

            b = QtWidgets.QPushButton('previous', self.currentDialogWindow)
            b.clicked.connect(self.previousDialog)
        return b

    def wizardComplete(self):
        self.currentDialogWindow.close()
