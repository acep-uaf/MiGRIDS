import shutil
import os
from PyQt5 import QtWidgets,QtSql
from UserInterface.Delegates import ClickableLineEdit, ComboDelegate
from UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from UserInterface.ModelSetupInformation import ModelSetupInformation
from UserInterface.ModelRunTable import RunTableModel
def switchProject(caller):
    '''saves an existing project, clears the database and initiates a new project'''
    saveProject(caller.model.setupFolder)
    print(type(caller))
    print(caller.objectName())
    del caller.model
    newmodel = ModelSetupInformation()
    clearProjectDatabase(caller)

    return newmodel

def saveProject(pathTo):
    '''saves the current project database to the specified path'''
    path = os.path.dirname(__file__)
    shutil.copy(os.path.join(path, '../project_manager'),
                os.path.join(pathTo, 'project_manager'))
    print('Database was saved to %s' % pathTo)
    return

def clearProjectDatabase(caller=None):
    handler = ProjectSQLiteHandler()
    # get the name of the last project worked on
    lastProjectPath = handler.getProjectPath()
    handler.makeDatabase()
    print(handler.dataCheck('components'))
    handler.closeDatabase()
    #the forms need to be cleared or data will get re-written to database
    if caller is not None:
        clearAppForms(caller)
    return lastProjectPath

def clearAppForms(caller):
    '''clears forms associated with the caller'''
    #param: caller [QtWidget] any form that is a child of the main window. All forms will be cleared
    win = caller.window()
    pageTabs = win.pageBlock
    for i in range(pageTabs.count()):
        form = pageTabs.widget(i)
        #clear the data input forms
        clearForms(form.findChildren(QtWidgets.QWidget))
    return
#recursive function to clear all forms.
def clearForms(listOfWidgets):
    if len(listOfWidgets) > 0:
        #clear a widget and all its children widgets then move to the next widget
        print(len(listOfWidgets))
        clearInputs(listOfWidgets[0])
        print(len(listOfWidgets))
        childs = listOfWidgets[0].findChildren(QtWidgets.QWidget)
        for c in childs:
            if c in listOfWidgets:
                listOfWidgets.remove(c)
        #listOfWidgets = listOfWidgets.remove(listOfWidgets[0].findChildren(QtWidgets.QWidget))
        print(len(listOfWidgets))
        #return clearForms(listOfWidgets[1:].remove(listOfWidgets[0].findChildren(QtWidgets.QWidget)))
        return clearForms(listOfWidgets[1:])
    else:
        return
def clearInputs(widget):
    #param: form [QtWidget] form containing input fields or SQL tables
    #remove tab, input and table children
    tabWidgets = widget.findChildren(QtWidgets.QTabWidget)
    for tw in tabWidgets:
        for t in range(1,tw.count()):
            tw.removeTab(t)
    inputs = widget.findChildren((QtWidgets.QLineEdit,QtWidgets.QTextEdit,
                                QtWidgets.QComboBox,ClickableLineEdit,ComboDelegate))

    for i in inputs:
        if type(i) in [QtWidgets.QLineEdit,QtWidgets.QTextEdit,ClickableLineEdit]:
            i.setText("")
        elif type(i) in [QtWidgets.QComboBox]:
            i.setCurrentIndex(0)
    tables = widget.findChildren(QtWidgets.QTableView)
    for t in tables:
        m=t.model()
        if type(m) is RunTableModel:
            m.clear()
        else:
            m.select()

