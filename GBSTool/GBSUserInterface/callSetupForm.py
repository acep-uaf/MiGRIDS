# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtCore, QtGui, QtWidgets,QtSql
from UISetupForm import SetupForm
from ConsoleDisplay import ConsoleDisplay

#This is what will be called by the controller

        
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('component_manager')

    s = SetupForm()

    sys.exit(app.exec_())

