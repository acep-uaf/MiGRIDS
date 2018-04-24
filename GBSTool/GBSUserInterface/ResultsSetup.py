from PyQt5 import QtWidgets, QtCore
class FormImportResult(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.init()
    #initialize the form
    def init(self):
        self.layout = QtWidgets.QGridLayout()
        self.plotWidget = self.createPlotArea()
        self.submitButton = self.createSubmitButton()

        self.layout.addWidget(self.plotWidget,0,0, 5,5)
        self.xcombo = self.createCombo(['field1'],True)
        self.ycombo = self.createCombo(['y1'], False)
        self.layout.addWidget(self.xcombo(6,3,1,1))
        self.layout.addWidget(self.ycombo(3,6,1,1))
        self.layout.addWidget(self.submitButton, 7,3,1,2)
        self.setLayout(self.layout)

    #List, Boolean -> QComboBox
    def createCombo(self,list,x):
        combo = QtWidgets.QComboBox(self)
        combo.addItems(list),
        if x:
            combo.objectName('xcombo')
        else:
            combo.objectName('ycombo')
        combo.currentIndexChanged().connect(self.currentIndexChanged)
        return combo

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
        #update the graph

    def createPlotArea(self):
        from ResultPlot import ResultPlot
        plotWidget = ResultPlot(self)

        return plotWidget
    def createSubmitButton(self):
        button = QtWidgets.QPushButton()

        return button