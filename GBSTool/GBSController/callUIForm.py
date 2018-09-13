# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtWidgets,QtSql,QtGui,QtCore
from GBSUserInterface.switchProject import clearProject
from GBSUserInterface.FormMain import MainForm

def callUIForm():
    '''call to show the user interface'''
    sys._excepthook = sys.excepthook
    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        print(exctype, value, traceback)
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)
    
    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    app = QtWidgets.QApplication(sys.argv)

    #start with an empty default database called project_manager
    #get the name of the last project worked on
    lastProjectPath = clearProject()

    #make the database available to the form models
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('project_manager')

    #launch the main form which contains subforms
    s = MainForm(lastProjectPath=lastProjectPath)

    try:
        sys.exit(app.exec_())

    except:
        print('exiting')

