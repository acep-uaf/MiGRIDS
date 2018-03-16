from PyQt5 import QtWidgets, QtGui, QtCore

class SetupWizard:
    #dialog sequence is a WizardTree containing info to be used when making dialog inputs
    def __init__(self, dialogSequence):
        self.dialogSequence = dialogSequence
        self.position = 0
        self.makeDialog(dialogSequence[self.position])

    #advances the wizard to the next dialog frame
    def nextDialog(self):
        self.currentDialog.close()
        self.position= self.dialogSequence.getNext()
        self.makeDialog(self.dialogSequence.getRecord(self.position))
        print('next')
        #return n
    #returns to the previous dialog frame
    def previousDialog(self):
        self.currentDialog.close()
        self.position = self.dialogSequence.getPrevious()
        self.makeDialog(self.dialogSequence.get(self.position))
        print('previous')
        #return p

    #makes a dialog box containing relevant information
    def makeDialog(self,d):

        self.currentDialog = QtWidgets.QDialog()
        self.currentDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.currentDialog.setWindowTitle(d['title'])
        vl = QtWidgets.QVBoxLayout()
        p =QtWidgets.QLabel(d['prompt'],self.currentDialog)
        vl.addWidget(p)
        vl.addStretch(2)
        hl = QtWidgets.QHBoxLayout()

        posButton = self.posButton()
        negButton = self.negButton()

        hl.addWidget(posButton)
        hl.addStretch(2)
        hl.addWidget(negButton)
        vl.addLayout(hl)
        self.currentDialog.setLayout(vl)
        self.currentDialog.exec()

    def posButton(self):
        #if we are at the last dialog then the positive button becomes a done button
        #otherwise it is the ok button
        try:
            self.dialogSequence[self.position + 1]
            b = QtWidgets.QPushButton('next', self.currentDialog)
            b.clicked.connect(self.nextDialog)
        except KeyError:
            b = QtWidgets.QPushButton('Done', self.currentDialog)
            b.clicked.connect(self.wizardComplete)
        return b

    def negButton(self):
        # if we are at the first dialog then the positive button becomes a cancel button
        # otherwise it is the previous button
        try:
            self.dialogSequence[self.position - 1]
            b = QtWidgets.QPushButton('previous', self.currentDialog)
            b.clicked.connect(self.previousDialog)
        except KeyError:
            b = QtWidgets.QPushButton('cancel', self.currentDialog)
            b.clicked.connect(self.wizardComplete)
        return b

    def wizardComplete(self):
        self.currentDialog.close()
