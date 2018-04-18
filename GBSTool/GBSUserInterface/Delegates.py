from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
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
#LineEdit textbox connected to the table
class TextDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent):
        QtWidgets.QItemDelegate.__init__(self,parent)

    def createEditor(self,parent, option, index):
        txt = QtWidgets.QLineEdit(parent)
        txt.inputMethodHints()
        txt.textChanged.connect(self.currentIndexChanged)
        return txt

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
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

class ComponentFormOpenerDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent):
        QtWidgets.QItemDelegate.__init__(self,parent)


    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            self.parent().setIndexWidget(
                index, QtWidgets.QPushButton('+',self.parent(), clicked=lambda:self.cellButtonClicked(index))
            )

    @QtCore.pyqtSlot()
    def cellButtonClicked(self, index):
        from formFromXML import formFromXML
        from UIToHandler import UIToHandler
        import os
        handler = UIToHandler()
        from Component import Component
        model = self.parent().model()
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
                                     pinmaxpa=model.data(model.index(index.row(), 8)),
                                     qinmaxpa=model.data(model.index(index.row(), 9)),
                                     qoutmaxpa=model.data(model.index(index.row(),10)),
                                     isvoltagesource=model.data(model.index(index.row(), 11))
                             )

        componentDict = component.toDictionary()
        print(componentDict)
        #the project filepath is stored in the model data for the setup portion
        #TODO fix. this works but is ugly and won't work if form changes structure
        mainForm  = self.parent().parent().parent().parent()

        setupInfo = mainForm.model
        setupInfo.setupFolder
        componentDir = os.path.join(setupInfo.setupFolder, '../Components')

        #tell the input handler to create or read a component descriptor and combine it with attributes in component
        componentSoup = handler.makeComponentDescriptor(component,componentDir)
        #data from the form gets saved to a soup, then written to xml
        #modify the soup to reflect data in the data model


        component.component_directory = componentDir
        f = formFromXML(component, componentSoup)


