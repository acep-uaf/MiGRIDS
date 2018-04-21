#class to create a console display to encorperate into a block of a user interface page
import logging

from PyQt5 import QtWidgets
from DisplayWriter import DisplayWriter, QtHandler

handler = QtHandler()

logger = logging.getLogger(__name__)
fmt = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class ConsoleDisplay(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ConsoleDisplay, self).__init__(parent)

        #the text block
        self._console = QtWidgets.QTextBrowser(self)
        #button block is in a new horizontal layout
        buttonGroup = QtWidgets.QGroupBox()
        buttonLayout = QtWidgets.QHBoxLayout()
        self._button = QtWidgets.QPushButton(self)
        self._button.setText('View Console')

        self._button2 = QtWidgets.QPushButton(self)
        self._button2.setText('Save Console Ouput')
        self._button.clicked.connect(self.hideDisplay)
        self._button2.clicked.connect(self.saveConsole)
        buttonLayout.addWidget(self._button)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self._button2)
        buttonGroup.setLayout(buttonLayout)

        #the console starts out invisible
        self._console.setVisible(False)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._console)
        layout.addWidget(buttonGroup)
        self.visible = False

        self.setLayout(layout)

        #connect to output class actions
        #DisplayWriter.stdout().messageWritten.connect(self._console.insertPlainText)
        #TODO uncomment when not testing otherwise fatal errors won't be seen
        #DisplayWriter.stderr().messageWritten.connect(self._console.insertPlainText)


        self.show()
        #self.raise_()

    def showMessage(self,msg):
        print(msg)

    #change the button text depending on whether or not the console is visible
    def switchWords(self):
        if self.visible:
            return 'View Console'
        return 'Hide Console'

    def saveConsole(self):
        import os
        import datetime
        #get save location with a file navigation dialog

        folderDialog = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a directory.', os.getcwd())

        #write text
        txt = self._console.toPlainText()

        #file gets named console_output_MMDDYY
        d = datetime.datetime.now()
        d = d.strftime('%m%d%y')
        #format d
        file = 'console_output_' + d + '.txt'
        file = os.path.join(folderDialog,file)
        with open(file, 'w+') as f:
            f.write(txt)

    def switchDisplay(self):
        if self.visible:
            self.visible = False
            self._console.setVisible(False)
        else:
            self.visible = True
            self._console.setVisible(True)

    def hideDisplay(self):
        txt = self.switchWords()
        self._button.setText(txt)
        self.switchDisplay()




