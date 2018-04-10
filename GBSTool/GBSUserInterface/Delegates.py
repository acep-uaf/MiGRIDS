from PyQt5 import QtCore, QtGui, QtWidgets
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

# #Button  connected to the table
# class ButtonDelegate(QtWidgets.QItemDelegate):
#     def __init__(self,parent,icon):
#         QtWidgets.QItemDelegate.__init__(self,parent)
#         self.icon = icon
#     def createEditor(self,parent, option, index):
#         button = QtWidgets.QPushButton(parent)
#         button.setIcon(button.style().standardIcon(getattr(QtWidgets.QStyle, self.icon)))
#         button.clicked.connect(self.currentIndexChanged)
#         return button
#     def setModelData(self, editor, model, index):
#         model.setData(index, editor.icon())
#
#     @QtCore.pyqtSlot()
#     def currentIndexChanged(self):
#         self.commitData.emit(self.sender())

# #Button  connected to the table
# class ComboDelegate(QtWidgets.QItemDelegate):
#     def __init__(self,parent,values):
#         QtWidgets.QItemDelegate.__init__(self,parent)
#         self.values = values
#
#     def createEditor(self,parent, option, index):
#         combo = QtWidgets.QComboBox(parent)
#         combo.addItems(self.values)
#         combo.currentIndexChanged.connect(self.currentIndexChanged)
#         return combo
#
#     def setEditorData(self, editor, index):
#         editor.blockSignals(True)
#
#         #set the combo to the selected index
#         print(index.model().data(index))
#         editor.setCurrentIndex(int(index.model().data(index)))
#         editor.blockSignals(False)
#
#     #write model data
#     def setModelData(self,editor, model, index):
#
#         model.setData(index, editor.itemText(editor.currentIndex()))
#
#
#     @QtCore.pyqtSlot()
#     def currentIndexChanged(self):
#
#         self.commitData.emit(self.sender())
