from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#plot widget
class ResultPlot(FigureCanvas):
    def __init__(self,parent):
        FigureCanvas.__init__(self, parent)

        fig  = Figure(figsize=(5,6), dpi = 100)

        self.axes = fig.add_subplot(111)
        self.figure = fig
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry()

        #data to plot
        self.data = {'x':[1,2,3,4,5,6,7],'y':[1,2,3,4,5,6,7]}
        #make plot
        self.makePlot()
    #make the plot
    def makePlot(self):

        ax = self.figure.add_Subplot(111)
        ax.clear()
        ax.plot(self.data, 'r_')
        ax.set_title('data plot')
        #refresh the plot
        self.draw()
        return

    #drop down menus for setting plot options
    def getOptions(self):
        return
