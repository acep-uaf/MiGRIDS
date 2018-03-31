
from plotSetResult import plotSetResult

plotRes = 'Wind Power Import kWh'
plotAttr = 'ees0.POutMaxPa.value'
otherAttr = ['gen0.POutMaxPa.value']
otherAttrVal = [[35,65]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\Igiugig0\OutputData\Set4'
baseSet = 2
baseRun = 0

plotSetResult(plotRes,plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal, baseSet = baseSet, baseRun = baseRun, subtractFromBase = False)