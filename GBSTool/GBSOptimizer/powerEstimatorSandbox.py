from matplotlib import pyplot as plt
import matplotlib.dates as md
import datetime
import pandas as pd
import netCDF4
import numpy as np
from scipy import stats, integrate
import seaborn as sns

'''Some helper routines to fix data'''


def fillTimeAndPowerVector(inptTime, spacing, inptPwr):
    outputTime = []
    outputPwr = []
    # Need to fill in gaps in the time vectors. Normally, time stamps are 15min (900 sec) apart, if this is not the case
    # missing time stamps need to be added.
    # This assumes good data in the first and last time stamp, and it does not check for equal spacing otherwise.
    for idx, ts in enumerate(inptTime):
        # Skip first entry, just use as is
        if idx == 0:
            print(['First: ', idx])
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])
        # Skip last entry, just use as is
        elif idx == inptTime.size-1:
            print(['Last: ', idx])
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])
        # Check if there is a gap greater 900 sec. If so, see how many multiples of 900 fit this gap and add these time
        # stamps.
        elif inptTime[idx+1] - ts > spacing:
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])
            dy = inptPwr[idx + 1] - inptPwr[idx]
            dx = inptTime[idx + 1] - ts
            slope = dy/dx
            print(['Used idx: ', idx])
            delta = int(np.floor((inptTime[idx+1] - ts)/spacing))
            print(inptTime[idx-1])
            print(inptTime[idx], ts)
            print(inptTime[idx+1])
            for i in range(1, delta):
                outputTime.append(inptTime[idx] + i*spacing)
                outputPwr.append(inptPwr[idx] + slope*i*spacing)
                print(i ,': Appending: ', inptTime[idx] + i*spacing, 'at ', idx)
        # All other cases, just take what's already there.
        else:
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])

    return outputTime, outputPwr


# import time series

# St. Mary's total load
nc = netCDF4.Dataset('../../GBSProjects/StMary/InputData/TimeSeriesData/RawData/StMaryTotalizerLoadkW.nc')
stmLoadPnc = nc.variables['value']
stmTime = np.asarray(nc.variables['time'])
stmLoadP = np.asarray(stmLoadPnc)
#stmLoadP = stmLoadP[0, :]
stmStart = datetime.datetime.fromtimestamp(stmTime[0,0])
stmEnd = datetime.datetime.fromtimestamp(stmTime[0,-1])
print(stmStart, stmEnd)

# Mt. Village's total load
nc = netCDF4.Dataset('../../GBSProjects/StMary/InputData/TimeSeriesData/RawData/MountainVillageTotalizerLoadkW.nc')
mtvLoadPnc = nc.variables['value']
mtvTime = np.asarray(nc.variables['time'])
mtvLoadP = np.asarray(mtvLoadPnc)
mtvLoadP = mtvLoadP[0, :]
mtvStart = datetime.datetime.fromtimestamp(mtvTime[0,0])
mtvEnd = datetime.datetime.fromtimestamp(mtvTime[0,-1])
mtvTime, mtvLoadP = np.array(fillTimeAndPowerVector(np.array(mtvTime[0, :]), 900, mtvLoadP))
print(mtvStart, mtvEnd)

stmLoadP = stmLoadP[stmTime > mtvTime[-35040] - 1]
stmTime = stmTime[stmTime > mtvTime[-35040] - 1]
stmStart = datetime.datetime.fromtimestamp(stmTime[0])

stmTime, stmLoadP = np.array(fillTimeAndPowerVector(stmTime, 900, stmLoadP))
print('Size before: ', mtvTime.size)
mtvTime = mtvTime[-35040:]
mtvLoadP = mtvLoadP[-35040:]
print('Size after: ', mtvTime.size)
mtvStart = datetime.datetime.fromtimestamp(mtvTime[0])
print(mtvStart)
stmDt = stmTime[1:] - stmTime[:-1]
mtvDt = mtvTime[1:] - mtvTime[:-1]

print(mtvTime.size)
print(stmTime.size)
print(stmStart)

timeStamps = [datetime.datetime.fromtimestamp(ts) for ts in stmTime]
mpTimeStamps = md.date2num(timeStamps)


plt.figure(figsize=(8, 5.5))
plt.subplots_adjust(bottom=0.2)
plt.xticks( rotation=25 )
ax=plt.gca()
xfmt = md.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(xfmt)
plt.plot(mpTimeStamps, mtvLoadP)
plt.plot(mpTimeStamps, stmLoadP)
plt.plot(mpTimeStamps, stmLoadP + mtvLoadP)
plt.savefig('StMarysAndMtVillageLoad.eps', format = 'eps')
plt.show()

'''
nc = netCDF4.Dataset('../../GBSProjects/StMary/InputData/TimeSeriesData/RawWindData/Calc55mPower.nc')
wtgPnc = nc.variables['value']
wtgTime3 = np.asarray(nc.variables['time'])
wtgP = np.asarray(wtgPnc)
wtgP[np.isnan(wtgP)] = -99
print(wtgP)'''

#plt.figure(figsize=(8.5, 5))
#plt.plot(snippetT, snippet)

#plt.show()

# create total load time series for the powerhouse
# if gen1P.size == gen2P.size:
#     genP = gen1P + gen2P
#     print('Same size')
# else:
#     print('Size mismatch gen1P and gen2P.')
#
# if genP.size == gen3P.size:
#     genP = genP + gen3P
#
# # produce distribution of differences
# dt = time1[1:] - time1[:-1]
# meanDt = np.mean(dt)
# dGenP = genP[1:] - genP[:-1]

#sns.distplot(dt)

'''
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
plt.show()'''

'''Helper routines go down here'''


