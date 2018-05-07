
import os

from PyQt5 import QtWidgets, QtCore
from GBSController.UIToHandler import UIToHandler



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
        #TODO data will always be None here?
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
                           newx = self.data.getattribute(s)[field]
                           self.displayData[s]['x'] = newx.values
                       else:
                           self.displayData[s]['x'] = self.data.index
                   else:
                       if field != 'index':
                            self.displayData[s]['y'] = self.data.getattribute(s)[field].values
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
        button.clicked.connect(self.refreshPlot)
        return button

    #refresh the data plot with currently set data
    def refreshPlot(self):
        self.data = self.parent().findChild(QtWidgets.QWidget, 'setupDialog').model.data
        if self.data is not None:

            #set the default data to display after fill options
            if 'displayData' not in self.__dict__.keys():
                self.displayData = self.defaultDisplay(self.data)
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

            options.append('index')
            self.xcombo.addItems(options)
            self.ycombo.addItems(options)
            self.displayData = self.defaultDisplay(data)
            self.plotWidget.makePlot(self.displayData)

    # ->QPushButton
    def createSubmitButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Generate netCDF inputs")
        button.clicked.connect(self.generateNetcdf)
        return button

    #uses the current data object to generate input netcdfs
    def generateNetcdf(self):

        handler = UIToHandler()
        #df gets read in from TimeSeries processed data folder
        #component dictionary comes from setupXML's
        MainWindow = self.window()
        setupForm = MainWindow.findChild(QtWidgets.QWidget,'setupDialog')
        setupModel= setupForm.model
        if 'setupFolder' in setupModel.__dict__.keys():
            setupFile = os.path.join(setupModel.setupFolder, setupModel.project + 'Setup.xml')
            componentModel = setupForm.findChild(QtWidgets.QWidget,'components').model()
            #From the setup file read the location of the input pickle
            #by replacing the current pickle with the loaded one the user can manually edit the input and
            #  then return to working with the interface
            data = handler.loadInputData(setupFile)
            df = data.fixed
            componentDict = {}
            if 'components' not in setupModel.__dict__.keys():
                #generate components
                setupForm.makeComponentList(componentModel)
            for c in setupModel.components:
                componentDict[c.component_name] = c.toDictionary()

            handler.createNetCDF(df, componentDict,setupFile)