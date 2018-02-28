import pandas as pd
from GBSAnalyzer.DataRetrievers.getDataChannels import getDataChannels
from GBSAnalyzer.DataRetrievers.getComponentTypeData import getComponentTypeData
from GBSAnalyzer.PerformanceAnalyzers.getFuelUse import getFuelUse

genAllP = getDataChannels('../../GBSProjects/Chevak/','InputData/TimeSeriesData/ProcessedData/',['gen1P', 'gen2P', 'gen3P'])
print(genAllP)
genAllMeta = getComponentTypeData('../../GBSProjects/Chevak/','Chevak', 'gen')

fuelCurveDataPoints = pd.DataFrame(genAllMeta[['fuelCurve_pPu', 'fuelCurve_massFlow', 'POutMaxPa']], index = genAllMeta.index)
genFuelUse = getFuelUse(genAllP, fuelCurveDataPoints)

print(genFuelUse)