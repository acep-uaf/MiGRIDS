# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from UISetupForm import SetupForm



        
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    s = SetupForm()
    sys.exit(app.exec_())

