from PyQt5 import QtWidgets


class ResultsOptimize(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.init()

    def init(self):
        self.layout = QtWidgets.QGridLayout()
        self.setObjectName("modelResult")

        self.refreshButton = self.createRefreshButton()
        # get the current data object
        # print(self.parent().parent().findChildren(QtWidgets.QWidget))

        # self.data = self.parent().findChild(QtWidgets.QWidget, 'modelDialog').model.data
        # temporary data
        self.data = {'runs': {'x': [1, 2, 3], 'y': [1, 2, 3]}}
        self.xcombo = self.createCombo([], True)
        self.ycombo = self.createCombo([], False)

        self.plotWidget = self.createPlotArea(self.data)
        self.layout.addWidget(self.plotWidget, 1, 0, 5, 5)
        self.layout.addWidget(self.refreshButton, 0, 0, 1, 2)
        self.layout.addWidget(self.xcombo, 7, 2, 1, 1)
        self.layout.addWidget(self.ycombo, 3, 6, 1, 1)

        self.setLayout(self.layout)
        self.showMaximized()
        return

    # ->plotWidget
    def createPlotArea(self, data):
        from GBSUserInterface.PlotResult import PlotResult
        plotWidget = PlotResult(self, data)
        return plotWidget

    # List, Boolean -> QComboBox
    def createCombo(self, list, x):
        combo = QtWidgets.QComboBox(self)
        combo.addItems(list),
        if x:
            combo.setObjectName('xcombo')
        else:
            combo.setObjectName('ycombo')
        combo.currentIndexChanged.connect(lambda: self.updatePlotData(combo.currentText(), combo.objectName()))
        return combo

    # updates the plot data but not the actual plot.
    # String, String -> None
    def updatePlotData(self, field, axis):
        # data is the data object
        if self.data is not None:
            if 'displayData' in self.__dict__.keys():
                for s in self.displayData.keys():
                    if axis == 'xcombo':
                        if field != 'index':
                            newx = self.data.getattribute(s)[field]
                            self.displayData[s]['x'] = newx.values
                        else:
                            self.displayData[s]['x'] = self.data.index
                    else:
                        if field != 'index':
                            self.displayData[s]['y'] = self.data.getattribute(s)[field].values
                        else:
                            self.displayData[s]['y'] = self.data.index
        return

    # ->QPushButton
    def createRefreshButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Refresh plot")
        button.clicked.connect(self.refreshPlot)
        return button

    # refresh the data plot with currently set data
    # None->None
    def refreshPlot(self):
        self.data = self.parent().findChild(QtWidgets.QWidget, 'setupDialog').model.data
        if self.data is not None:

            # set the default data to display after fill options
            if 'displayData' not in self.__dict__.keys():
                self.displayData = self.defaultDisplay(self.data)
        else:
            self.displayData = None
        self.plotWidget.makePlot(self.displayData)
        return