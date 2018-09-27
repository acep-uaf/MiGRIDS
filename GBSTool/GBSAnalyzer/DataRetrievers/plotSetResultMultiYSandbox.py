
from GBSTool.GBSAnalyzer.DataRetrievers.plotSetResultMultipleY import plotSetResult


plotResValues = [{'Generator Output [GWh]':[{'Direct import and GBS charging, ':{'Generator Import kWh':'+', 'Generator Charging kWh':'+',1000000:'/'}},{'Direct import, ':{'Generator Import kWh':'+',1000000:'/'}}]},
                 {'Wind Turbine Output [GWh]':[{'Direct import, GBS charging and SLC output, ':{'Thermal Energy Storage Throughput kWh': '+', 'Wind Power Import kWh': '+',
                                            'Wind Power Charging kWh': '+', 1000000: '/'}},{'Direct import and GBS charging, ':{'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'}}]}]

# subtract from base: 0 - do not subtract or add, but if base case is specified, place at the begining
# 1 - subtract value from base -> decrease from base case
# 2 - subtract base from value -> increase from base case

subtractFromBase = [0]*len(plotResValues)

plotAttr = 'ees0.ratedDuration.value'
plotAttrName = 'GBS Rated Duration (s)'
otherAttr = ['ees0.POutMaxPa.value']
otherAttrNames = {'ees0.POutMaxPa.value':'GBS Rated Power (kW)'}
otherAttrVal = [[500,750,1000]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\OutputData\Set19b'
baseSet =  17
baseRun =  0
for pRV, sFB in zip(plotResValues,subtractFromBase):
    plotResName, plotRes = zip(*pRV.items())
    plotSetResult(plotRes[0],plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal,
                  baseSet = baseSet, baseRun = baseRun, subtractFromBase = sFB, removeSingleOtherAttr = True,
                  alwaysUseMarkers = True, plotResName= plotResName[0], plotAttrName = plotAttrName,
                  otherAttrNames = otherAttrNames)