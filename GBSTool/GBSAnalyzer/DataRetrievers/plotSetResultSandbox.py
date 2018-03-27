
from plotSetResult import plotSetResult

plotRes = 'Energy Storage SRC kWh'
plotAttr = 'ees0.POutMaxPa.value'
otherAttr = ['gen0.POutMaxPa.value']
otherAttrVal = [[35,65]]
projecSetDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\Igiugig0\OutputData\Set4'

plotSetResult(plotRes,plotAttr, projectSetDir = projecSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal)