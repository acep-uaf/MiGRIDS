#Form for display model run parameters
from PyQt5 import QtWidgets
from makeButtonBlock import makeButtonBlock
from tableHandler import tableHandler
class ModelRunForm(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setObjectName("modelRun")
        self.runTable = createRunTable()
        #Todo look up run table name
        self.buttonBlock = self.dataButtons('runs')
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.buttonBlock)
        self.layout.addWidget(self.runTable)
        self.setLayout(self.layout)
        self.showMaximized()

    def createRunTable(self):
        return

    # string -> QGroupbox
    def dataButtons(self, table):
        handler = tableHandler(self)
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()


        # buttonRow.addWidget(self.makeBlockButton(self.functionForLoadDescriptor,
        #                                          None, 'SP_DialogOpenButton',
        #                                          'Load a previously created model.'))

        buttonRow.addWidget(makeButtonBlock(self,lambda: handler.functionForNewRecord(table),
                                                 '+', None,
                                                 'Add a component'))
        buttonRow.addWidget(makeButtonBlock(self,lambda: handler.functionForDeleteRecord(table),
                                                 None, 'SP_TrashIcon',
                                                 'Delete a component'))
        buttonRow.addStretch(3)
        buttonBox.setLayout(buttonRow)
        return buttonBox