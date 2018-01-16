from matplotlib import pyplot as plt
import pandas as pd
import netCDF4
import numpy as np
from scipy import stats, integrate
import seaborn as sns


# import generator load time series
nc = netCDF4.Dataset('../../GBSProjects/Chevak/InputData/TimeSeriesData/ProcessedData/gen1P.nc')
gen1Pnc = nc.variables['value']
time1 = np.asarray(nc.variables['time'])
gen1P = np.asarray(gen1Pnc)

nc = netCDF4.Dataset('../../GBSProjects/Chevak/InputData/TimeSeriesData/ProcessedData/gen2P.nc')
gen2Pnc = nc.variables['value']
time2 = nc.variables['time']
gen2P = np.asarray(gen2Pnc)
print(gen2P)

nc = netCDF4.Dataset('../../GBSProjects/Chevak/InputData/TimeSeriesData/ProcessedData/gen3P.nc')
gen3Pnc = nc.variables['value']
time3 = nc.variables['time']
gen3P = np.asarray(gen3Pnc)

# create total load time series for the powerhouse
if gen1P.size == gen2P.size:
    genP = gen1P + gen2P
    print('Same size')
else:
    print('Size mismatch gen1P and gen2P.')

if genP.size == gen3P.size:
    genP = genP + gen3P

# produce distribution of differences
dt = time1[1:] - time1[:-1]
meanDt = np.mean(dt)
dGenP = genP[1:] - genP[:-1]

#sns.distplot(dt)


# Demo plot of loss of wind farm scenario
time = np.array(range(120))
wtgP = np.zeros(time.size, 'int')
wtgP[:15] = 100
essP = np.zeros(time.size, 'int')
x = 100 - 2 * np.array(range(15))
essP[15:30] = x
essP[30:40] = essP[29]
essP[40:60] = essP[39] - 35
x1 = essP[59] - (essP[59]/15)*np.array(range(15))
essP[60:75] = x1
genP = np.zeros(time.size, 'int')
genP[:15] = 120
genP[15:30] = 120 - x + 100
genP[30:60] = genP[29]
genP[60:75] = genP[59] - x1 + essP[59]
genP[75:] = genP[74]




plt.figure(figsize=(8, 5.5))
plt.plot(time, wtgP)
plt.plot(time, essP)
plt.plot(time, genP)
plt.savefig('lossOfWindDemo.eps', format = 'eps')
plt.show()