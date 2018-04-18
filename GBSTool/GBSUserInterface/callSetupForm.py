# -*- coding: utf-8 -*-
#
import sys
from PyQt5 import QtCore, QtGui, QtWidgets,QtSql
from UISetupForm import SetupForm
from formFromXML import formFromXML
from ConsoleDisplay import ConsoleDisplay

#This is what will be called by the controller

# sys._excepthook = sys.excepthook
#
# def my_exception_hook(excepttype,value,traceback):
#     print(excepttype,value,traceback)
#     sys.excepthook(excepttype,value,traceback)
#     sys.exit(1)
#
# sys.excepthook = my_exception_hook

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    #start with an empty database
    from ComponentSQLiteHandler import SQLiteHandler
    handler = SQLiteHandler('component_manager')
    handler.makeDatabase()

    #make the database available to the form models
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('component_manager')

    s = SetupForm()
    try:
        sys.exit(app.exec_())
    except:
        print('exiting')

