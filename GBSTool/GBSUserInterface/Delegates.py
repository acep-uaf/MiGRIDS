from PyQt5 import QtCore, QtWidgets, QtSql
class ComboReference():
    def __init__(self,cmb,table,db):
        self.cmb = cmb
        self.table = table
        self.db = db
        self.values = self.getValues()
        self.valueCodes = self.getCodes()

    def getValues(self):
        values = self.db.getRefInput(self.table)
        values.insert(0,'Select - Select')
        return values
    def getCodes(self):
        return [self.parseCombo(x) for x in self.values]
    def parseCombo(self, inputString):
        code = inputString.split(" - ")[0]
        description = inputString.split(" - ")[1]
        return code, description

    def valuesAsDict(self):

        d={}
        for v in self.values:
            code,description = self.parseCombo(v)
            d[code]=description

        return d
class ComboDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent,values):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.values = values


    def createEditor(self,parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.setObjectName('components')
        combo.setModel(self.values)
        combo.currentIndexChanged.connect(self.currentIndexChanged)

        return combo

    def makeList(self,box, values):

        self.values = values
        for i in range(box.count()):
            box.removeItem(i)
        box.addItems(self.values)

    def setEditorData(self, editor, index):
        editor.blockSignals(True)

        #set the combo to the selected index
        editor.setCurrentText(index.model().data(index))
        editor.blockSignals(False)

    #write model data
    def setModelData(self,editor, model, index):

        model.setData(index, editor.itemText(editor.currentIndex()))

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


#LineEdit textbox connected to the table
class TextDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent):
        QtWidgets.QItemDelegate.__init__(self,parent)
        if 'column1' in parent.__dict__.keys():
            self.autotext1 = parent.column1

    def createEditor(self,parent, option, index):
        txt = QtWidgets.QLineEdit(parent)
        txt.inputMethodHints()
        txt.textChanged.connect(self.currentIndexChanged)
        return txt

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        if 'autotext1' in self.__dict__.keys():
            editor.setText(self.autotext1)
        else:
            editor.setText(str(index.model().data(index)))

        editor.blockSignals(False)

    def setModelData(self, editor, model, index):

        model.setData(index, editor.text())

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

class RelationDelegate(QtSql.QSqlRelationalDelegate):
    def __init__(self, parent):
        QtSql.QSqlRelationalDelegate.__init__(self,parent)


    def setModelData(self,editor, model, index):

        model.setData(index, editor.itemText(editor.currentIndex()))
    @QtCore.pyqtSlot()
    def currentIndexChanged(self):

        self.commitData.emit(self.sender())

class ClickableLineEdit(QtWidgets.QLineEdit):
    clicked = QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        else:
            super().mousePressEvent(event)

class TextBoxWithClickDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent, text,fn):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.text = text

    def createEditor(self,parent, option, index):
        #Line Edit Object
        txt = ClickableLineEdit(parent)
        txt.clicked.connect(lambda: self.cellButtonClicked(index))
        self.parent().setIndexWidget(index, txt)
        return txt

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        #displayed text gets set to model text value
        editor.setText(str(index.model().data(index)))

        editor.blockSignals(False)

    def setModelData(self, editor, model, index):

        model.setData(index, editor.text())

    @QtCore.pyqtSlot()
    def cellButtonClicked(self, index):
        from DialogComponentList import ComponentSetListForm
        from ProjectSQLiteHandler import ProjectSQLiteHandler
        #get the data model
        model = self.parent().model()
        # get the cell, and open a listbox of possible components for this project
        checked = model.data(model.index(index.row(), 2))
        # checked is a comma seperated string but we need a list
        checked = checked.split(',')
        listDialog = ComponentSetListForm(checked)
        components = listDialog.checkedItems()
        #format the list to be inserted into a text field in a datatable
        str1 = ','.join(components)

        model.setData(index, str1)
        #TODO reomove temporary debug code
        sqlhandler = ProjectSQLiteHandler('project_manager')
        print(sqlhandler.cursor.execute("select * from sets").fetchall())
        sqlhandler.closeDatabase()
        #submit the model data to the database
        model.submitAll()
        #requery the database table
        model.select()


class ComponentFormOpenerDelegate(QtWidgets.QItemDelegate):

    def __init__(self,parent,text):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.text = text


    def paint(self, painter, option, index):

        if not self.parent().indexWidget(index):

            self.parent().setIndexWidget(
                index, QtWidgets.QPushButton(self.text,self.parent(), clicked=lambda:self.cellButtonClicked(index))
            )


    @QtCore.pyqtSlot()
    def cellButtonClicked(self, index):
        from formFromXML import formFromXML
        from UIToHandler import UIToHandler
        from ModelSetTable import SetTableModel
        from ModelComponentTable import  ComponentTableModel
        from FormSetup import FormSetup
        import os

        handler = UIToHandler()
        from Component import Component

        model = self.parent().model()
        #if its a component table bring up the component editing form
        if type(model) is ComponentTableModel:
            #if its from the component table do this:
            #there needs to be a component descriptor file written before this form can open
            #column 0 is id, 3 is name, 2 is type

            #make a component object from these model data
            component =Component(component_name=model.data(model.index(index.row(), 3)),
                                         original_field_name=model.data(model.index(index.row(), 1)),
                                         units=model.data(model.index(index.row(), 4)),
                                         offset=model.data(model.index(index.row(), 6)),
                                         type=model.data(model.index(index.row(), 2)),
                                         attribute=model.data(model.index(index.row(), 7)),
                                         scale=model.data(model.index(index.row(), 5)),

                                 )

            #componentDict = component.toDictionary()

            #the project filepath is stored in the model data for the setup portion
            #TODO fix. this works but is ugly and won't work if form changes structure
            mainForm  = self.parent().parent().parent().parent()

            setupInfo = mainForm.model
            setupInfo.setupFolder
            componentDir = os.path.join(setupInfo.setupFolder, '../Components')

            #TODO check if component type has been set
            #tell the input handler to create or read a component descriptor and combine it with attributes in component
            componentSoup = handler.makeComponentDescriptor(component.component_name,componentDir)
            #data from the form gets saved to a soup, then written to xml
            #modify the soup to reflect data in the data model


            component.component_directory = componentDir
            f = formFromXML(component, componentSoup)
        elif type(model) is SetTableModel:
            pageBlock = self.parent().parent().parent().parent().parent().parent().parent().parent()
            mainForm = pageBlock.findChild(FormSetup)

            setupInfo = mainForm.model
            component_name = model.data(model.index(index.row(), 2))
            if ('setupFolder' in setupInfo.getAttributes()) & (component_name != ''):
                 #look for a local component file

                componentDir = os.path.join(setupInfo.setupFolder, '../Components')
                component = Component(component_name=component_name)

                # tell the input handler to create or read a component descriptor and combine it with attributes in component
                componentSoup = handler.makeComponentDescriptor(component.component_name, componentDir)
                # data from the form gets saved to a soup, then written to xml
                # modify the soup to reflect data in the data model

                component.component_directory = componentDir
                f = formFromXML(component, componentSoup,False)
            else:
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Component Name",
                                            "You need to select a component before editing attributes.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()

