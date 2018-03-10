# -*- coding: utf-8 -*-
#
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDialog
from UISetupForm import UISetupForm

def callSetupForm():
    class AppWindow(QDialog):
        def __init__(self):
            super().__init__()
            #set the main setup form class
            self.ui = UISetupForm()
            self.ui.setupUi(self)
            self.show()
            
    app = QApplication(sys.argv)
    w=AppWindow()
    
    sys.exit(app.exec_())