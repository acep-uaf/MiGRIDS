# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from UISetupForm import UISetup

        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    ex = UISetup()
    sys.exit(app.exec_())