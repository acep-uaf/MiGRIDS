
from GBSTool.GBSAnalyzer.DataRetrievers.plotSetResult import plotSetResult

plotRes = ['Wind Power Import kWh','Generator Import kWh','Generator Switching','Generator Loading','Diesel-off time h',
           'Generator Cumulative Run time h','Generator Cumulative Capacity Run Time kWh','Generator Overloading Time h',
           'Generator Overloading kWh','Wind Power Import kWh','Wind Power Spill kWh','Energy Storage Discharge kWh',
           'Energy Storage SRC kWh','Energy Storage Overloading Time h','Energy Storage Overloading kWh',
           'Thermal Energy Storage Throughput kWh']

plotResValues = {'Wind Power Import [kWh]':'Wind Power Import kWh','Generator Import [kWh]':'Generator Import kWh',
                 'Generator Switching':'Generator Switching','Generator Loading':'Generator Loading','Diesel-off time [h]':'Diesel-off time h',
           'Generator Cumulative Run time [h]':'Generator Cumulative Run time h',
                 'Generator Cumulative Capacity Run Time [kWh]':'Generator Cumulative Capacity Run Time kWh','Generator Overloading Time [h]':'Generator Overloading Time h',
           'Generator Overloading [kWh]':'Generator Overloading kWh','Wind Power Import [kWh]':'Wind Power Import kWh',
                 'Wind Power Spill [kWh]':'Wind Power Spill kWh','GBS Discharge [kWh]':'Energy Storage Discharge kWh',
           'GBS SRC Provided [kWh]':'Energy Storage SRC kWh','GBS Overloading Time [h]':'Energy Storage Overloading Time h','GBS Overloading [kWh]':'Energy Storage Overloading kWh',
           'Thermal Energy Storage Throughput [kWh]':'Thermal Energy Storage Throughput kWh',
                 'Total Generator Output [kWh]':{'Generator Import kWh':'+', 'Generator Charging kWh':'+'},
                 'Total Wind Output [kWh]':{'Thermal Energy Storage Throughput kWh':'+', 'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+'},
                 'Total Wind Output (Electrical Loads) [kWh]':{'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+'},
                 'GBS Equivalent Cycles':{'Energy Storage Discharge kWh':'+', 'ees0.PInMaxPa.value':'/'}}

subtractFromBase = [False,True,True,False,False,
                    True,True,False,
                    False,False,True,False,
                    False,False,False,True,True,False]
subtractFromBase = [True]*len(plotRes)

plotAttr = 'ees0.ratedDuration.value'
plotAttrName = 'GBS Rated Duration (s)'
plotResName, plotRes = zip(*plotResValues.items())
otherAttr = ['ees0.POutMaxPa.value']
otherAttrNames = {'ees0.POutMaxPa.value':'GBS Rated Power (kW)'}
otherAttrVal = [[500,750,1000]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\OutputData\Set16'
baseSet = 17
baseRun = 0
for pR,pRN, sFB in zip(plotRes,plotResName,subtractFromBase):
    plotSetResult(pR,plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal,
                  baseSet = baseSet, baseRun = baseRun, subtractFromBase = sFB, removeSingleOtherAttr = True,
                  alwaysUseMarkers = True, plotResName= pRN, plotAttrName = plotAttrName,
                  otherAttrNames = otherAttrNames)