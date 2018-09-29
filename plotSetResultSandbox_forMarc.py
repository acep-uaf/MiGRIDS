
from GBSTool.GBSAnalyzer.DataRetrievers.plotSetResult import plotSetResult

plotResValues = {
                 'Total Wind Output [GWh]':{'Thermal Energy Storage Throughput kWh':'+', 'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'},
                 'Total Wind Output (Electrical Loads) [GWh]':{'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'} }

# subtract from base: 0 - do not subtract or add, but if base case is specified, place at the begining
# 1 - subtract value from base -> decrease from base case
# 2 - subtract base from value -> increase from base case

subtractFromBase = [0]*len(plotResValues)

saveNames = ['WindOutputSubset.png','WindOutputSubsetElectrical.png']
plotAttr = 'ees0.ratedDuration.value'
plotAttrName = 'GBS Rated Duration (s)'
plotResName, plotRes = zip(*plotResValues.items())
otherAttr = ['ees0.POutMaxPa.value']
otherAttrNames = {'ees0.POutMaxPa.value':'GBS Rated Power (kW)'}
otherAttrVal = [[500,750,1000]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\OutputData\Set16a'
baseSet =  ''
baseRun =  ''
for pR,pRN, sFB, saveName in zip(plotRes,plotResName,subtractFromBase,saveNames):
    plotSetResult(pR,plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal,
                  baseSet = baseSet, baseRun = baseRun, subtractFromBase = sFB, removeSingleOtherAttr = True,
                  alwaysUseMarkers = True, plotResName= pRN, plotAttrName = plotAttrName,
                  otherAttrNames = otherAttrNames,saveName=saveName)