
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

        self.refreshButton = self.createRefreshButton()
        #get the current data object
        #print(self.parent().parent().findChildren(QtWidgets.QWidget))

        self.data = None

        #self.displayData = {'fixed': {'x': None, 'y': None}, 'raw': {'x': None, 'y': None}}
        #TODO data will always be None here?

        self.xcombo = self.createCombo([], True)
        self.ycombo = self.createCombo([], False)

        self.plotWidget = self.createPlotArea(self.data)
        self.layout.addWidget(self.plotWidget, 1, 0, 5, 5)
        self.layout.addWidget(self.refreshButton, 0,0,1,2)
        self.layout.addWidget(self.xcombo,7,2,1,1)
        self.layout.addWidget(self.ycombo,3,6,1,1)

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
                           newx = self.data[s][field]
                           self.displayData[s]['x'] = newx.values
                       else:
                           self.displayData[s]['x'] = self.data[s].index
                   else:
                       if field != 'index':
                            self.displayData[s]['y'] = self.data[s][field].values
                       else:
                           self.displayData[s]['y'] = self.data[s].index


    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
        #update the graph

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    #->plotWidget
    def createPlotArea(self,data):
        from GBSUserInterface.PlotResult import PlotResult
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

        if self.data is not None:
            #set the default data to display after fill options
            if 'displayData' not in self.__dict__.keys():
                self.displayData = self.defaultDisplay(self.data)
        else:
            self.displayData = None
        self.plotWidget.makePlot(self.displayData)

    #data object consisting of fixed and raw dataframes
    def defaultDisplay(self):

        displayData = {'raw': {'x':self.data['raw'].index, 'y':self.data['raw']['total_p']},
                       'fixed': {'x':self.data['fixed'].index, 'y':self.data['fixed'].total_p}
                       }
        return displayData

    def defaultPlot(self):
        if self.data is not None:
           # combo boxes need to be set with field options
            options = list(self.data['fixed'].columns.values)

            options.append('index')
            self.xcombo.addItems(options)
            self.ycombo.addItems(options)
            self.displayData = self.defaultDisplay()
            self.plotWidget.makePlot(self.displayData)

    def setPlotData(self,data):
        '''sets the data attribute
        :param data [DataClass] is the data to be available for use in plots'''
        def mergedDF(lodf):
            df0 = lodf[0]
            for d in lodf[1:]:
                df0 = df0.append(d)
            return df0
        self.data = {'raw':data.raw,'fixed':mergedDF(data.fixed)}

