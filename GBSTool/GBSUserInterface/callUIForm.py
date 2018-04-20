# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtCore, QtGui, QtWidgets,QtSql
from UISetupForm import SetupForm
from MainForm import MainForm

#This is what will be called by the controller



if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    #start with an empty default database
    from ProjectSQLiteHandler import ProjectSQLiteHandler
    handler = ProjectSQLiteHandler('project_manager')
    handler.makeDatabase()

    #make the database available to the form models
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('project_manager')

    s = MainForm()
    try:
        sys.exit(app.exec_())
    except:
        print('exiting')

