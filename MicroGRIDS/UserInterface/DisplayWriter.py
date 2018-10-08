#class for writing console output to a widget
import sys
import logging
from PyQt5 import QtCore

class DisplayWriter(QtCore.QObject):
    _stdout = None
    _stderr = None

    messageWritten = QtCore.pyqtSignal(str)

    def flush(self):
        pass
    def fileno(self):
        return -1
    def write(self, msg):
        if (not self.signalsBlocked()):
            self.messageWritten.emit(msg)

    #set the screen to be written to the ConsoleDisplay
    @staticmethod
    def stdout():
        if( not DisplayWriter._stdout):
            DisplayWriter._stdout = DisplayWriter()
            sys.stdout = DisplayWriter._stdout
        return DisplayWriter._stdout

    @staticmethod
    def stderr():
        if (not DisplayWriter._stderr):
            DisplayWriter._stderr = DisplayWriter()
            sys.stderr = DisplayWriter._stderr
        return DisplayWriter._stderr

class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
    def emit(self, msg):
        msg = self.format(msg)
        if msg:
            DisplayWriter.stdout().write('%s \n' %msg)