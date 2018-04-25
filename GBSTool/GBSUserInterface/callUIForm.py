# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtCore, QtGui, QtWidgets,QtSql
from FormSetup import FormSetup
from FormMain import MainForm

#This is what will be called by the controller
sys._excepthook = sys.excepthook
def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    #start with an empty default database
    from ProjectSQLiteHandler import ProjectSQLiteHandler
    handler = ProjectSQLiteHandler('project_manager')
    #handler.makeDatabase()

    #make the database available to the form models
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('project_manager')

    s = MainForm()
    try:
        sys.exit(app.exec_())
    except:
        print('exiting')

