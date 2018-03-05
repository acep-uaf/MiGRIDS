from GBSAnalyzer.DataRetrievers.getComponentTypeData import getComponentTypeData
from GBSAnalyzer.DataRetrievers.getDataChannels import getDataChannels
from GBSAnalyzer.PerformanceAnalyzers.getLoadFactor import getLoadFactor

genAllP = getDataChannels('../../GBSProjects/Chevak/','InputData/TimeSeriesData/ProcessedData/',['gen1P', 'gen2P', 'gen3P'])
genAllP['time'] = genAllP['time']/1000000000
genAllMeta = getComponentTypeData('../../GBSProjects/Chevak/','Chevak', 'gen')

#fuelCurveDataPoints = pd.DataFrame(genAllMeta[['fuelCurve_pPu', 'fuelCurve_massFlow', 'POutMaxPa']], index = genAllMeta.index)
#genFuelUse, fuelStats = getFuelUse(genAllP, fuelCurveDataPoints)

genAllPPu = getLoadFactor(genAllP, genAllMeta['POutMaxPa'])

"""
print(type(genFuelUse))
plt.figure(figsize=(8, 5.5))
plt.plot(genFuelUse['time'], genFuelUse['gen1'])

plt.show()
"""