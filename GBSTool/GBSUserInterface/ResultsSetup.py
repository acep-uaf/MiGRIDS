
import os
import pickle
from PyQt5 import QtWidgets, QtCore
from UIToHandler import UIToHandler
from readXmlTag import readXmlTag


class ResultsSetup(QtWidgets.QWidget):
    def __init__(self,parent):
        super().__init__(parent)

        self.init()
    #initialize the form
    def init(self):
        self.layout = QtWidgets.QGridLayout()
        self.setObjectName("setupResult")
        self.submitButton = self.createSubmitButton()
        self.refreshButton = self.createRefreshButton()
        #get the current data object
        #print(self.parent().parent().findChildren(QtWidgets.QWidget))

        self.data = self.parent().findChild(QtWidgets.QWidget,'setupDialog').model.data
        #self.displayData = {'fixed': {'x': None, 'y': None}, 'raw': {'x': None, 'y': None}}
        if self.data is not None:
            self.xcombo = self.createCombo((self.data.fixed.columns).append('index'), True)
            self.ycombo = self.createCombo((self.data.fixed.columns).append('index'), False)
        else:
            self.xcombo = self.createCombo([], True)
            self.ycombo = self.createCombo([], False)

        self.plotWidget = self.createPlotArea(self.data)
        self.layout.addWidget(self.plotWidget, 1, 0, 5, 5)
        self.layout.addWidget(self.refreshButton, 0,0,1,2)
        self.layout.addWidget(self.xcombo,7,2,1,1)
        self.layout.addWidget(self.ycombo,3,6,1,1)
        self.layout.addWidget(self.submitButton, 8,2,1,2)
        self.setLayout(self.layout)


    #List, Boolean -> QComboBox
    def createCombo(self,list,x):
        combo = QtWidgets.QComboBox(self)
        combo.addItems(list),
        if x:
            combo.setObjectName('xcombo')
        else:
            combo.setObjectName('ycombo')
        combo.currentIndexChanged.connect(lambda: self.updatePlotData(combo.currentText(),combo.objectName()))
        return combo

    def updatePlotData(self, field, axis):
        #data is the data object
        if self.data is not None:
            if 'displayData' in self.__dict__.keys():
                for s in self.displayData.keys():
                   if axis == 'xcombo':
                       if field != 'index':
                           self.displayData[s]['x'] = self.data.getattribute(s)[field]
                       else:
                           self.displayData[s]['x'] = self.data.index
                   else:
                       if field != 'index':
                            self.displayData[s]['y'] = self.data.getattribute(s)[field]
                       else:
                           self.displayData[s]['y'] = self.data.index


    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
        #update the graph

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    #->plotWidget
    def createPlotArea(self,data):
        from PlotResult import PlotResult
        plotWidget = PlotResult(self, data)
        return plotWidget

    #->QPushButton
    def createRefreshButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Refresh plot")
        button.clicked.connect(lambda: self.refreshPlot(self.data))
        return button

    #refresh the data plot with currently set data
    def refreshPlot(self, data):
        self.data = data
        if data is not None:


            #set the default data to display after fill options
            if 'dsiplayData' not in self.__dict__.keys():
                self.displayData = self.defaultDisplay(data)
        else:
            self.displayData = None
        self.plotWidget.makePlot(self.displayData)

    #data object consisting of fixed and raw dataframes
    def defaultDisplay(self, data):
        import pandas as pd
        displayData = {'raw': {'x':pd.to_datetime(data.raw.DATE, unit='s'), 'y':data.raw['total_p']},
                       'fixed': {'x': data.fixed.index, 'y': data.fixed.total_p}
                       }
        return displayData
    def defaultPlot(self, data):
        if data is not None:
            # combo boxes need to be set with field options
            options = list(data.fixed.columns.values)

            self.xcombo.addItems(options)
            self.ycombo.addItems(options)
            self.displayData = self.defaultDisplay(data)
            self.plotWidget.makePlot(self.displayData)

    # ->QPushButton
    def createSubmitButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Generate netCDF inputs")
        button.clicked.connect(lambda: self.parent.onClick(self.generateNetcdf))
        return button

    #uses the current data object to generate input netcdfs
    def generateNetcdf(self):

        handler = UIToHandler()
        #df gets read in from TimeSeries processed data folder
        #component dictionary comes from setupXML's
        MainWindow = self.parent().parent()
        setupModel = MainWindow.findChild(QtWidgets.QtWidget,'setupDialog').model
        setupFile = os.path.join(setupModel.setupFolder, setupModel.project + 'Setup.xml')
        #From the setup file read the location of the input pickle
        #by replacing the current pickle with the loaded one the user can manually edit the input and
        #  then return to working with the interface
        #TODO xml reading should be moved to controller
        inputDirectory = readXmlTag(setupFile, 'inputFileDir', 'value')
        inputDirectory = os.path.join(*inputDirectory)
        outputDirectory = os.path.join(inputDirectory, '/ProcessedData')

        dataFile = os.path.join(outputDirectory,'processed_input_file.pkl')
        data = pickle.load(dataFile,'b')
        df = data.fixed
        componentDict = {}
        for c in setupModel.components:
            componentDict[c] = c.toDictionary()
        handler.createNetCDF(df, componentDict,None,setupFile)