from PyQt5 import QtCore, QtWidgets, QtSql
from GBSInputHandler.Component import Component
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
import os
#class for combo boxes that are not derived from database relationships
class ComboDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent,values, name=None):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.values = values
        self.name = name

    def createEditor(self,parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.setObjectName(self.name)
        combo.setModel(self.values)
        #combo.currentIndexChanged.connect(self.currentIndexChanged)
        combo.activated.connect(self.currentIndexChanged)
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
        from GBSUserInterface.getComponentAttributesAsList import getComponentAttributesAsList
        self.commitData.emit(self.sender())
        #if its the sets table then the attribute list needs to be updated
        if self.name == 'componentName':
            tv = self.parent()
            cbs = tv.findChildren(ComboDelegate)
            for cb in cbs:
                if cb.name == 'componentAttribute':
                    lm = cb.values
                    #populate the combo box with the possible attributes that can be changed

                    # project folder is from FormSetup model
                    projectFolder = tv.window().findChild(QtWidgets.QWidget, "setupDialog").model.projectFolder
                    componentFolder = os.path.join(projectFolder, 'InputData', 'Components')
                    #the current selected component, and the folder with component xmls are passed used to generate tag list
                    lm.setStringList(getComponentAttributesAsList(self.sender().currentText(),componentFolder))

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

#combo boxes for tables with foreign keys
class RelationDelegate(QtSql.QSqlRelationalDelegate):
    def __init__(self, parent,name):
        QtSql.QSqlRelationalDelegate.__init__(self,parent)
        self.parent = parent
        self.name=name

    def createEditor(self, parent, option, index):
        #make a combo box if there is a valid relation
        if index.model().relation(index.column()).isValid:
            editor = QtWidgets.QComboBox(parent)
            editor.activated.connect(self.currentIndexChanged)
            return editor
        else:
            return QtWidgets.QStyledItemDelegate(parent).createEditor(parent,option,index)

    def setEditorData(self, editor, index):
        m = index.model()
        relation = m.relation(index.column())
        if relation.isValid():
            pmodel = QtSql.QSqlTableModel()
            pmodel.setTable(relation.tableName())
            pmodel.select()
            editor.setModel(pmodel)
            editor.setModelColumn(pmodel.fieldIndex(relation.displayColumn()))
            editor.setCurrentIndex(editor.findText(m.data(index)))

    def setModelData(self,editor, model, index):
         model.setData(index, editor.itemText(editor.currentIndex()))



    @QtCore.pyqtSlot()
    def currentIndexChanged(self):

        self.commitData.emit(self.sender())
        #if a type from the components table was just set then fill in the component name unless it is already named
        if (self.name == 'component_type') & (self.parent.objectName() == 'components'):
            #get the table view object
            tv = self.parent
            #combo is the combo box that is sending these data
            combo = self.sender()
            #current row
            currentRow = tv.indexAt(combo.pos()).row()

            #check if there is already a component name
            currentName = tv.model().data(tv.model().index(currentRow,3))
            if (currentName == '') | (currentName is None) | (currentName == 'NA') | (currentName[0:3] != self.sender().currentText()):
                #get the number of components of this type -
                handler = ProjectSQLiteHandler()
                i = handler.getTypeCount(self.sender().currentText())
                handler.closeDatabase()
                name = self.sender().currentText() + str(i)

                tv.model().setData(tv.model().index(currentRow,3),name)
                tv.model().submitAll()
                tv.model().select()
            return
#QLineEdit that when clicked performs an action
class ClickableLineEdit(QtWidgets.QLineEdit):
    clicked = QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        else:
            super().mousePressEvent(event)


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
        from GBSController.UIToHandler import UIToHandler
        from ModelSetTable import SetTableModel
        from ModelComponentTable import  ComponentTableModel
        from FormSetup import FormSetup
        import os

        handler = UIToHandler()

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
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Component Name",
                                            "You need to select a component before editing attributes.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

