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
    totDataPntsAdded = 0
    # Need to fill in gaps in the time vectors. Normally, time stamps are 15min (900 sec) apart, if this is not the case
    # missing time stamps need to be added.
    # This assumes good data in the first and last time stamp, and it does not check for equal spacing otherwise.
    for idx, ts in enumerate(inptTime):
        # Skip first entry, just use as is
        if idx == 0:
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])
        # Skip last entry, just use as is
        elif idx == inptTime.size - 1:
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])
        # Check if there is a gap greater 900 sec. If so, see how many multiples of 900 fit this gap and add these time
        # stamps.
        elif inptTime[idx + 1] - ts > spacing:
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])
            dy = inptPwr[idx + 1] - inptPwr[idx]
            dx = inptTime[idx + 1] - ts
            slope = dy / dx
            delta = int(np.floor((inptTime[idx + 1] - ts) / spacing))
            for i in range(1, delta):
                outputTime.append(inptTime[idx] + i * spacing)
                outputPwr.append(inptPwr[idx] + slope * i * spacing)
                totDataPntsAdded = totDataPntsAdded + 1
        # All other cases, just take what's already there.
        else:
            outputTime.append(ts)
            outputPwr.append(inptPwr[idx])

    print('Total data points added : ', totDataPntsAdded)
    return outputTime, outputPwr


'''LoadData helps with repeatedly loading data from well formed netCDF files, i.e., such files with a 'value' 'time'
    tuple. 
    THIS ROUTINE IGNORES SCALING AT THIS POINT
'''


def loadData(filePath):
    nc = netCDF4.Dataset(filePath)
    value = np.asarray(nc.variables['value'])
    time = np.asarray(nc.variables['time'])

    # simplify
    value = value[0, :]
    time = time[0, :]
    timeStamps = [datetime.datetime.fromtimestamp(ts) for ts in time]

    startDate = datetime.datetime.fromtimestamp(time[0])
    endDate = datetime.datetime.fromtimestamp(time[-1])

    return value, time, timeStamps, startDate, endDate


# import time series

# St. Mary's total load
stmLoadP, stmTime, stmTimeStamps, stmStart, stmEnd = loadData(
    '../../GBSProjects/StMary/InputData/TimeSeriesData/RawData/StMaryTotalizerLoadkW.nc')

# Mt. Village's total load
mtvLoadP, mtvTime, mtvTimeStamps, mtvStart, mtvEnd = loadData(
    '../../GBSProjects/StMary/InputData/TimeSeriesData/RawData/MountainVillageTotalizerLoadkW.nc')
print('Patching Mt. Village Data...') #Needs to be patched first to yield useable master timestamp vector
mtvTime, mtvLoadP = np.array(fillTimeAndPowerVector(np.array(mtvTime[:]), 900, mtvLoadP))

# Clip Mt. Village TS to one year length using most recent year
mtvTime = mtvTime[-35040:]
mtvLoadP = mtvLoadP[-35040:]
mtvStart = datetime.datetime.fromtimestamp(mtvTime[0])
print('Mt. Village data set clipped to: Start date : ', mtvStart, ' End date: ', mtvEnd)
stmDt = stmTime[1:] - stmTime[:-1]
mtvDt = mtvTime[1:] - mtvTime[:-1]

# Adjust length of stmLoadP and stmTime vectors based on available data in Mt. Village TS
stmLoadP = stmLoadP[stmTime > mtvTime[-35040] - 1]
stmTime = stmTime[stmTime > mtvTime[-35040] - 1]
stmStart = datetime.datetime.fromtimestamp(stmTime[0])
print('St. Mary\'s data set clipped to: Start date : ', stmStart, ' End date: ', stmEnd)

print('Patching St. Mary\'s Data...')
stmTime, stmLoadP = np.array(fillTimeAndPowerVector(stmTime, 900, stmLoadP))
# Need to fix time stamps vector
stmTimeStamps = [datetime.datetime.fromtimestamp(ts) for ts in stmTime]

# Calculate total combined load
print('Calculating total combined load...')
totLoadP = stmLoadP + mtvLoadP
print('Average combined load: ', np.nanmean(totLoadP), ' kW')
print('Standard deviation from average: ', np.nanstd(totLoadP), ' kW')



# Wind power data set
wtgP, wtgTime, wtgTimeStamps, wtgStart, wtgEnd = loadData(
    '../../GBSProjects/StMary/InputData/TimeSeriesData/RawWindData/Calc50mPowerDW52.nc')

# fix any data gaps
print('Patching wind power data...')
wtgTime, wtgP = np.array(fillTimeAndPowerVector(wtgTime, 600, wtgP))

# Need to reorganize the time series so that it starts where the load time-series start
# Entries 0 through 11520 need to appended at the end
wtgTime1 = wtgTime[:11521]
wtgTime2 = wtgTime[11521:]
wtgTime = np.append(wtgTime1, wtgTime2, axis=0)
wtgP1 = wtgP[:11521]
wtgP2 = wtgP[11521:]
wtgP = np.append(wtgP1, wtgP2, axis=0)
# Cut down to one year length
wtgP = wtgP[:52560]
wtgPSize10 = wtgP.size


# need to resample the time series to fit with the load data
# get actual time stamps
wtgTimeStamps = [datetime.datetime.fromtimestamp(ts) for ts in wtgTime[:52560]]
wtgSeries = pd.Series(wtgP, index=wtgTimeStamps)
wtgShrt = wtgSeries.resample('15T').mean()

wtgP = np.array(wtgShrt)
# Fill NaN with 0
wtgP[np.isnan(wtgP)] = 0
print('Wind power data set re-sampled from 10 to 15 min intervals. Size changed from: ', wtgPSize10, 'to ', wtgP.size)


genP = totLoadP - wtgP
genDP = (genP[1:] - genP[:-1]) / (15 * 60)



plt.figure(figsize=(8, 5.5))


# discretize the profile
# Generator fleet as per 'Saint-Marys-REF8' project file
gen1PMax = 499 #Cummins QSX15G9
gen2PMax = 611 #Caterpillar 3508
gen3PMax = 908 #Caterpillar 3512
MOL = 0#.15 # NOTE THE FILE SUPPLIED BY AVEC STATES 0% (!!!)

# Minimum spinning reserve kept in the system
# NOTE: this is a brute force approach, but with data available better estimates are not possible.
srcP = 0#.15*np.nanmean(totLoadP)

print('Assuming SRC : ', srcP, 'kW')

# isolate the data where there is more wind power than demand.
curtailedP = np.copy(genP)
curtailedP[genP > MOL * gen1PMax] = np.nan
curtailedP = -(curtailedP - MOL * gen1PMax)

# Curtailment condition
genP[genP < MOL*gen1PMax] = MOL*gen1PMax # Normal approach with MOL
#genP[genP < 0] = 0 # Low load diesel, with 0 kW possible

# Find which generator is online based on generator loading
genPAvail = np.zeros(np.shape(genP))
chngCnt = 0

for i, p in enumerate(genP):
    if p < MOL*gen1PMax:
        genPAvail[i] = 0
    elif p < (gen1PMax - srcP):
        genPAvail[i] = gen1PMax
    elif p < (gen2PMax - srcP):
        genPAvail[i] = gen2PMax
    elif p < (gen3PMax - srcP):
        genPAvail[i] = gen3PMax
    elif p < (gen1PMax + gen2PMax - srcP):
        genPAvail[i] = gen1PMax + gen2PMax
    else:
        genPAvail[i] = -100

    if chngCnt > 0 and (genPAvail[i]-genPAvail[i-1] < 0):
        genPAvail[i] = genPAvail[i-1]

    # Prevent excessive down transitions
    if i > 3:
        if (genPAvail[i] - genPAvail[i-1]) < 0:
            chngCnt = 4
        elif chngCnt > 0:
            chngCnt = chngCnt - 1
        else:
            chngCnt = 0

print('Number of diesel configuration changes : ', np.sum(np.abs(np.sign(np.diff(genPAvail)))))

# Capacity factor
nonZeroGenPAvail = np.copy(genPAvail)
nonZeroGenPAvail[genPAvail == 0] = np.nan
print('Diesel capacity factor :', np.nanmean(genP/nonZeroGenPAvail))
print('Diesel kWh total: ', np.nansum(genP)/4)

print('Wind power curtailed :', np.nansum(curtailedP)/4, ' kWh')

essEMaxRng = [1, 10, 100, 200, 500, 750, 1000, 2500, 5000, 10000, 12500, 15000, 17500, 20000, 25000]
wpRec = np.zeros(np.shape(essEMaxRng))
essPMax = 500


for j, essEMax in enumerate(essEMaxRng):
    essEIn = np.zeros(np.shape(curtailedP))
    essEIn[0] = 0#curtailedP[0] / 4
    essEOut = np.zeros(np.shape(curtailedP))
    essEOut[0] = 0
    essP = np.zeros(np.shape(curtailedP))
    essETot = 0 #0.5*essEMax
    SOC = np.zeros(np.shape(curtailedP))
    recoveredWtgE = 0
    expendedWtgE = 0

    for idx, wp in enumerate(curtailedP[1:]):
        SOC[idx] = essETot/essEMax
        if wp > 0 and essETot < essEMax:
            essEOut[idx] = 0
            dE = (essEMax - essETot)
            if wp/4 < dE:
                essEIn[idx] = essEIn[idx-1] + (wp/4)
                essP[idx] = -wp
                recoveredWtgE = recoveredWtgE + (wp/4)
                essETot = essETot + (wp/4)
            else:
                essEIn[idx] = essEIn[idx - 1] + dE
                essP[idx] = -dE
                recoveredWtgE = recoveredWtgE + dE
                essETot = essETot + dE
        elif np.isnan(wp) and essETot > 10:
            essEIn[idx] = 0
            # if possible discharge at full power
            if genP[idx] > essPMax and essETot > essPMax/4:
                essETot = essETot - (essPMax/4)
                #print('Full power; essETot = ', essETot)
                essEOut[idx] = essEOut[idx - 1] + (essPMax/4)
                essP[idx] = essPMax
                expendedWtgE = expendedWtgE + (essPMax/4)
            elif genP[idx] < essPMax and essETot > genP[idx]/4:
                essETot = essETot - (genP[idx]/4)
                essP[idx] = genP[idx]
                #print('Reduced power; essETot = ', essETot)
                essEOut[idx] = essEOut[idx - 1] + (genP[idx] / 4)
                expendedWtgE = expendedWtgE + (genP[idx]/4)
            else:
                essEOut[idx] = essEOut[idx - 1] + essETot
                essP[idx] = 4*essETot
                expendedWtgE = expendedWtgE + essETot
                #print('Remaining power; essETot = ', essETot)
                essETot = 0


    print('ESS cummulative kWh in: ', recoveredWtgE)
    print('ESS cummulative kWh out: ', expendedWtgE)
    wpRec[j] = recoveredWtgE


# Matplotlib formated timestamps for plotting routines.
mpTimeStamps = md.date2num(stmTimeStamps)


print((np.nansum(curtailedP) / 4) / (np.nansum(wtgP) / 4), (np.nansum(wtgP) / 4))
'''#plt.plot(mpTimeStamps, genP)
#plt.plot(mpTimeStamps, genPAvail)
#plt.plot(mpTimeStamps, curtailedP)
plt.plot(mpTimeStamps, genP)
plt.plot(mpTimeStamps, essP)
#plt.plot(essEMaxRng, wpRec/1000)
plt.show()

curtailedP[np.isnan(curtailedP)] = 0
curtailedPD = (curtailedP[1:] - curtailedP[:-1])/4


sns.distplot(curtailedPD)'''


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

# sns.distplot(dt)

plt.subplots_adjust(bottom=0.2)
plt.xticks(rotation=25)
ax = plt.gca()
xfmt = md.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(xfmt)
#plt.plot(mpTimeStamps, mtvLoadP)
#plt.plot(mpTimeStamps, stmLoadP)
#plt.plot(mpTimeStamps, totLoadP)
#plt.plot(mpTimeStamps, wtgP)
#plt.plot(mpTimeStamps, genP)
#plt.hist(genP, bins='auto')
#plt.savefig('StMarysAndMtVillageLoad.eps', format = 'eps')
plt.plot(mpTimeStamps, totLoadP)
plt.xlabel('Time')
plt.ylabel('Total system load [kW]')
plt.savefig('totalSystemLoad.eps', format = 'eps')
'''
vals, base = np.histogram(genDP, bins=150)
cumDist = np.cumsum(vals)
plt.plot(base[:-1], cumDist/genP.size)'''
plt.show()

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
