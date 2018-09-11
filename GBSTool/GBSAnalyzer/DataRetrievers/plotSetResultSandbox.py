
from GBSTool.GBSAnalyzer.DataRetrievers.plotSetResult import plotSetResult

plotResValues = {'Generator Import [GWh]':{'Generator Import kWh':'+',1000000:'/'},'Generator Charging [kWh]':{'Generator Charging kWh':'+',1000000:'/'},
                 'Generator Switching':'Generator Switching','Generator Loading':'Generator Loading','Diesel-off time [h]':'Diesel-off time h',
           'Generator Cumulative Run time [h]':'Generator Cumulative Run time h',
                 'Generator Cumulative Capacity Run Time [GWh]':{'Generator Cumulative Capacity Run Time kWh':'+',1000000:'/'},'Generator Overloading Time [h]':'Generator Overloading Time h',
           'Generator Overloading [kWh]':'Generator Overloading kWh','Wind Power Import [GWh]':{'Wind Power Import kWh':'+',1000000:'/'},'Wind Power Charging [MWh]':{'Wind Power Charging kWh':'+',1000:'/'},
                 'Wind Power Spill [GWh]':{'Wind Power Spill kWh':'+',1000000:'/'},'GBS Discharge [MWh]':{'Energy Storage Discharge kWh':'+',1000:'/'},
           'GBS SRC Provided [GWh]':{'Energy Storage SRC kWh':'+',1000000:'/'},'GBS Overloading Time [h]':'Energy Storage Overloading Time h','GBS Overloading [kWh]':'Energy Storage Overloading kWh',
           'Thermal Energy Storage Throughput [GWh]':{'Thermal Energy Storage Throughput kWh':'+',1000000:'/'},
                 'Total Generator Output [GWh]':{'Generator Import kWh':'+', 'Generator Charging kWh':'+',1000000:'/'},
                 'Total Wind Output [GWh]':{'Thermal Energy Storage Throughput kWh':'+', 'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'},
                 'Total Wind Output (Electrical Loads) [GWh]':{'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'},
                 'GBS Equivalent Cycles':{'Energy Storage Discharge kWh':'+', 'ees0.PInMaxPa.value':'/'},'Mean Individual Online Generator Capacity [kW]':{'Generator Cumulative Capacity Run Time kWh':'+','Generator Cumulative Run time h':'/'}}

# subtract from base: 0 - do not subtract or add, but if base case is specified, place at the begining
# 1 - subtract value from base -> decrease from base case
# 2 - subtract base from value -> increase from base case

subtractFromBase = [0]*len(plotResValues)

plotAttr = 'ees0.ratedDuration.value'
plotAttrName = 'GBS Rated Duration (s)'
plotResName, plotRes = zip(*plotResValues.items())
otherAttr = ['ees0.POutMaxPa.value']
otherAttrNames = {'ees0.POutMaxPa.value':'GBS Rated Power (kW)'}
otherAttrVal = [[500,750,1000]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\OutputData\Set16a'
baseSet =  17
baseRun =  0
for pR,pRN, sFB in zip(plotRes,plotResName,subtractFromBase):
    plotSetResult(pR,plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal,
                  baseSet = baseSet, baseRun = baseRun, subtractFromBase = sFB, removeSingleOtherAttr = True,
                  alwaysUseMarkers = True, plotResName= pRN, plotAttrName = plotAttrName,
                  otherAttrNames = otherAttrNames)