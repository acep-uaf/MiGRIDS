
from GBSTool.GBSAnalyzer.DataRetrievers.plotSetResult import plotSetResult

plotRes = ['Wind Power Import kWh','Generator Import kWh','Generator Switching','Generator Loading','Diesel-off time h',
           'Generator Cumulative Run time h','Generator Cumulative Capacity Run Time kWh','Generator Overloading Time h',
           'Generator Overloading kWh','Wind Power Import kWh','Wind Power Spill kWh','Energy Storage Discharge kWh',
           'Energy Storage SRC kWh','Energy Storage Overloading Time h','Energy Storage Overloading kWh',
           'Thermal Energy Storage Throughput kWh']
subtractFromBase = [False,True,True,False,False,
                    True,True,False,
                    False,False,True,False,
                    False,False,False,True]
plotAttr = 'ees0.ratedDuration.value'
plotAttrName = 'GBS Rated Duration (s)'
otherAttr = ['ees0.POutMaxPa.value']
otherAttrNames = {'ees0.POutMaxPa.value':'GBS Rated Power (kW)'}
otherAttrVal = [[500,750,1000]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\OutputData\Set8'
baseSet = 6
baseRun = 0
for pR, sFB in zip(plotRes,subtractFromBase):
    plotSetResult(pR,plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal,
                  baseSet = baseSet, baseRun = baseRun, subtractFromBase = sFB, removeSingleOtherAttr = True,
                  alwaysUseMarkers = True, plotAttrName = plotAttrName, otherAttrNames = otherAttrNames)