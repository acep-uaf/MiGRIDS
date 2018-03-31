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
        # logging.getLogger().addHandler(self._console)
        # logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # logging.getLogger().setLevel(logging.DEBUG)
        self._button = QtWidgets.QPushButton(self)
        self._button.setText('View Console')

        self._console.setVisible(False)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._console)
        layout.addWidget(self._button)
        self.visible = False

        self.setLayout(layout)

        #connect to output class actions
        DisplayWriter.stdout().messageWritten.connect(self._console.insertPlainText)
        DisplayWriter.stderr().messageWritten.connect(self._console.insertPlainText)

        self._button.clicked.connect(self.hideDisplay)
        self.show()
        self.raise_()

    def showMessage(self,msg):
        print(msg)

    #change the button text depending on whether or not the console is visible
    def switchWords(self):
        if self.visible:
            return 'View Console'
        return 'Hide Console'
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
        #TODO remove test print statements
        print ('This is the console. Messages will appear here.')
        #logging messages also appear in the console
        logger.debug('logging and error messages also appear here')



