
from MicroGRIDS.InputHandler.fixDataIntervalTransitionMatrix import fixDataIntervalTransitionMatrix
from MicroGRIDS.InputHandler.fixDataInterval import fixDataInterval
from MicroGRIDS.Analyzer.PerformanceAnalyzers.rainfallCounting import rainflow
from MicroGRIDS.InputHandler.fixBadData import DataClass
import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
import datetime
import scipy.fftpack
import copy
import os
from netCDF4 import Dataset
import pickle


### constants
saveLocation = 'C:\\Users\\jbvandermeer\\Documents\\ACEP\\GBS\\TimeSeriesSynthesis\\BenchMarkPerformance\\Figures'
timeNow = datetime.datetime.now().strftime("%Y %m %d %H %M %S")

'''
#### create a sine wave ###
Fs = 1/(60*15) # sampling freq: once every 15 min
t = np.arange(1000)*(60*15) # time steps every 15 min
f = 1/(60*60*24) # wave frequency: every 24 hours
values = np.sin(2 * np.pi * f * t)*100
# repeat to get high temperal res values
Fs_highRes = 1
t_highRes = np.arange(int(len(t)*Fs_highRes/Fs))*1/Fs_highRes # time steps every 15 min
values_highRes =  np.sin(2 * np.pi * f * t_highRes)*100

# datetime
base = pd.datetime.today()
date_list = pd.to_datetime([base + pd.Timedelta(seconds=x/Fs) for x in range(0, len(t))])
date_list_highRes = pd.to_datetime([base + pd.Timedelta(seconds=x/Fs_highRes) for x in range(0, len(t_highRes))])

# add some gaussian noise
mu = 50
sigma = 20
for idx in range(len(values)):
    values[idx] += random.gauss(mu=mu, sigma=sigma) - mu/2
'''
#### grab Igiugig data ####

# cd to Igiugig data
here = os.path.dirname(os.path.realpath(__file__))
os.chdir(here)
os.chdir('..\..\GBSProjects\Igiugig0\InputData\TimeSeriesData\ProcessedData')
# totalizer load, 15 min averages
rootgrp = Dataset('load0P.nc', "r", format="NETCDF4")
# number of desired data points
N = len(rootgrp.variables['time'][0]) # sample size
date_list = pd.to_datetime(rootgrp.variables['time'][0][:N],unit='s')
values = rootgrp.variables['value'][0][:N]

# make low res data
Ts = np.mean(np.diff(date_list)) / np.timedelta64(1,'s')  # mean sampling period in seconds of input data
Fs = 1/Ts # sampling frequency
TsLowRes = 15*60 # low res sampling period
FsLowRes = 1/TsLowRes # low res sampling frquency
TsRatio = int(TsLowRes/Ts) # ratio between sampling periods
idx = 0
valuesLowRes = []
date_listLowRes = []
while idx < len(values):
    valuesLowRes += [values[idx]]
    date_listLowRes += [date_list[idx]]
    idx = idx + TsRatio


### initiate data class ###

raw_df = pd.DataFrame({'date': date_listLowRes, 'gen1': valuesLowRes, 'gen2':valuesLowRes},index=date_listLowRes)
dfHighRes = pd.DataFrame({'date': date_list, 'gen1': values, 'gen2':values},index=date_list)
# create a dataclass object
A = DataClass(raw_df, FsLowRes)
A.powerComponents = ['gen1','gen2']
A.totalPower()
# copy A so can test with Markov later on
Acopy = copy.copy(A)
# create a high res data class
AHighRes = DataClass(dfHighRes,Fs)
AHighRes.powerComponents = ['gen1','gen2']
AHighRes.totalPower()

# save
os.chdir(saveLocation)
pickleOut = open("OriginalResults"+timeNow+".p", "wb")
pickle.dump(AHighRes.fixed,pickleOut)
pickleOut.close()

### test Langevin upsampling ###
# test effect of sample period on std

# find average std per 15 min period
'''
sigmaList = []
meanList = []
#for idx in range(np.min([int((len(AHighRes.raw.total_p)-(15*60))/(15*60)),100000])):
for idx in range(len(A.raw.total_p)): # for each low res value
    sigmaList += [np.std(AHighRes.raw.total_p[idx*15*60:(idx+1)*15*60])]
    meanList += [np.mean(AHighRes.raw.total_p[idx*15*60:(idx+1)*15*60])]
sigma = np.nanmean(sigmaList)
sigmaFromLowRes = A.raw.total_p.rolling(10, 1).std() # for comparing with other sigma calculation
sigmaFromLowRes[0] = sigmaFromLowRes[1]
#sigma = sigmaFromLowRes*1.5
sigmaMuRatio = sigmaList[:-1]/np.abs(np.diff(A.raw.total_p))
meanSigmaMuRatio = np.mean(sigmaMuRatio)
plt.plot(sigmaFromLowRes,sigmaList,'.',markersize = 1)
# compare pdfs of rolling 15 min and 1 sec data
bins = np.linspace(np.min([np.min(sigmaList),np.min(sigmaFromLowRes)]), np.max([np.max(sigmaList),np.max(sigmaFromLowRes)]),20)
histSigma1sec = np.histogram(sigmaList, bins = bins)
histSigma15min = np.histogram(sigmaFromLowRes, bins = bins)
xPdf = bins[:-1]
barWidth = np.min(np.diff(bins))/3
plt.figure()
plt.bar(xPdf,histSigma1sec[0]/sum(histSigma1sec[0])*100,barWidth)
plt.bar(xPdf + barWidth,histSigma15min[0]/sum(histSigma15min[0])*100, barWidth)
plt.ylabel('Probability [%]')
plt.xlabel('Standard Deviation')
plt.legend(['STD of 1 sec values in a 15 min period','Rolling STD of the 10 past 15 min values'])

sigma = None
#sigma = np.std(AHighRes.raw.total_p)
df = fixDataIntervalTransitionMatrix(A,'1s', sigma, stdNum = 5)
print('Calculated Langevin Data')
plt.figure()
plt.plot(df.fixed.total_p)
plt.plot(df.raw.total_p,'*-')
plt.plot(AHighRes.raw.total_p)
#plt.show()

#save data
os.chdir(saveLocation)
pickleOut = open("LangevinResults"+timeNow+".p", "wb")
pickle.dump(df.fixed,pickleOut)
pickleOut.close()

#pickle.dump(df,open("LangevinResults"+timeNow+".p", "wb"))

# test frequency distribution
# get the fft of input data
yf_in = scipy.fftpack.fft(values)
N_in = len(date_list)
xf_in = np.linspace(0.0, 0.5*Fs, int(N_in/2))
# get fft of output data
yf_out = scipy.fftpack.fft(df.fixed.gen1)
N_out = len(df.fixed.gen1)
xf_out = np.linspace(0.0, 0.5*1, int(N_out/2))

# plot fft
plt.figure()
plt.plot(xf_in, 2.0/N_in * np.abs(yf_in[:int(N_in/2)]))
plt.plot(xf_out, 2.0/N_out * np.abs(yf_out[:int(N_out/2)]))

#plt.show()
'''
### Test Markov ###
print('precalculating transition matrix')
# get transition matrix of differences from the moving average
from GBSAnalyzer.DataRetrievers.getTimeSeriesTransitionMatrix import getTransitionMatrix
window = TsRatio # make the window size the number of steps inbetween the low res data steps
valuesMovAve = AHighRes.raw.total_p.rolling(window).mean()
valuesMovAve = valuesMovAve.bfill()
valuesDiff = AHighRes.raw.total_p - valuesMovAve

# upsample the low res data linearly.
x = range(len(values))
xLowRes = np.linspace(0,len(values),len(Acopy.raw.total_p))
valuesInterp = np.interp(x, xLowRes, Acopy.raw.total_p)
valuesDiff = AHighRes.raw.total_p - valuesInterp
print('caculating transition matrix')
tm, tmValues = getTransitionMatrix(valuesDiff,numStates=100)

print('Got Transition Matrix')
sigma = None
dfMarkov = fixDataIntervalTransitionMatrix(Acopy,'1s', sigma, True, tm, tmValues, stdNum = 5)

print('Synthesized Markov Data')

# save
os.chdir(saveLocation)
pickleOut = open("MarkovResults"+timeNow+".p", "wb")
pickle.dump(dfMarkov.fixed,pickleOut)
pickleOut.close()

#pickle.dump(df,open("MarkovResults"+timeNow+".p", "wb"))

plt.figure()
plt.plot(dfMarkov.fixed.total_p)
plt.plot(df.fixed.total_p)
plt.plot(dfMarkov.raw.total_p,'*-')
plt.plot(date_list,values*2)
plt.legend(['Markov','Langevin','Original Low Res','Original High Res'])
plt.ylabel('kW')
plt.savefig('timeSeries '+timeNow+'.png')
plt.show()

# test frequency distribution
# get fft of output data
yf_outMarkov = scipy.fftpack.fft(dfMarkov.fixed.gen1)
N_outMarkov = len(dfMarkov.fixed.gen1)
xf_outMarkov = np.linspace(0.0, 0.5*1, int(N_out/2))

# plot fft
plt.figure()
plt.plot(xf_in[1:], 2.0/N_in * np.abs(yf_in[1:int(N_in/2)]))
plt.plot(xf_out[1:], 2.0/N_out * np.abs(yf_out[1:int(N_out/2)]))
plt.plot(xf_outMarkov[1:], 2.0/N_out * np.abs(yf_outMarkov[1:int(N_out/2)]))
plt.legend(['Langevin','Original','Markov'])
plt.savefig('fft '+timeNow+'.png')
plt.show()

### autocorrelation
# look at up to > 1 day lag
lagList = np.linspace(0,100000,99)
originalAC = [] # original data
# Langevin data
langAC = []
# Markov data
markAC = []
for lag in lagList:
    originalAC += [AHighRes.raw.total_p.autocorr(int(int(lag)))]
    langAC += [df.fixed.total_p.autocorr(int(int(lag)))]
    markAC += [dfMarkov.fixed.total_p.autocorr(int(int(lag)))]

# save
os.chdir(saveLocation)
pickle.dump(originalAC,open("originalAC"+timeNow+".p", "wb"))
pickle.dump(langAC,open("langAC"+timeNow+".p", "wb"))
pickle.dump(markAC,open("markAC"+timeNow+".p", "wb"))

# plot
plt.figure()
plt.plot(lagList/3600,originalAC)
plt.plot(lagList/3600,langAC)
plt.plot(lagList/3600,markAC)
plt.legend(['Original','Langevin','Markov'])
plt.xlabel('hours')
plt.ylabel('Autocorrelation')
plt.show()
os.chdir(saveLocation)
plt.savefig('AutoCorrelation '+timeNow+'.png')
#plt.savefig('AutoCorrelation.png')


# look at around 30 min lag
lagList = np.linspace(0, 2000, 100)
originalAC = []  # original data
# Langevin data
langAC = []
# Markov data
markAC = []
for lag in lagList:
    originalAC += [AHighRes.raw.total_p.autocorr(int(int(lag)))]
    langAC += [df.fixed.total_p.autocorr(int(int(lag)))]
    markAC += [dfMarkov.fixed.total_p.autocorr(int(int(lag)))]

# save
os.chdir(saveLocation)
pickle.dump(originalAC,open("originalACZoom"+timeNow+".p", "wb"))
pickle.dump(langAC,open("langACZoom"+timeNow+".p", "wb"))
pickle.dump(markAC,open("markACZoom"+timeNow+".p", "wb"))

# plot
plt.figure()
plt.plot(lagList/60, originalAC)
plt.plot(lagList/60, langAC)
plt.plot(lagList/60, markAC)
plt.legend(['Original', 'Langevin', 'Markov'])
plt.xlabel('minutes')
plt.ylabel('Autocorrelation')
os.chdir(saveLocation)
plt.show()
plt.savefig('AutoCorrelationZoom '+timeNow+'.png')
#plt.savefig('AutoCorrelationZoom.png')


### power spectral density

plt.subplot(211)
plt.plot(date_list,values*2)
plt.plot(df.fixed.total_p)
plt.plot(dfMarkov.fixed.total_p)
plt.legend(['Original','Langevin','Markov'])
plt.ylabel('kW')
plt.subplot(212)
origPSD = plt.psd(AHighRes.raw.total_p,256,1)
langPSD = plt.psd(df.fixed.total_p,256,1)
markPSD = plt.psd(dfMarkov.fixed.total_p,256,1)
plt.savefig('psd '+timeNow+'.png')
plt.show()

plt.figure()
plt.psd(AHighRes.raw.total_p,256,1)
plt.psd(df.fixed.total_p,256,1)
plt.psd(dfMarkov.fixed.total_p,256,1)
plt.legend(['Original','Langevin','Markov'])
plt.ylabel('kW')
plt.savefig('psdZoom '+timeNow+'.png')
plt.show()

# save
os.chdir(saveLocation)
pickle.dump(origPSD,open("origPSD"+timeNow+".p", "wb"))
pickle.dump(langPSD,open("langPSD"+timeNow+".p", "wb"))
pickle.dump(markPSD,open("markPSD"+timeNow+".p", "wb"))



### pdf

bins = np.linspace(np.min(AHighRes.raw.total_p)*0.8, np.max(AHighRes.raw.total_p)*1.2,20)
histOrig = np.histogram(AHighRes.raw.total_p, bins = bins)
histLang = np.histogram(df.fixed.total_p,bins = bins)
histMarkov = np.histogram(dfMarkov.fixed.total_p,bins = bins)

# save
os.chdir(saveLocation)
pickle.dump(histOrig,open("histOrig"+timeNow+".p", "wb"))
pickle.dump(histLang,open("histLang"+timeNow+".p", "wb"))
pickle.dump(histMarkov,open("histMarkov"+timeNow+".p", "wb"))

xPdf = bins[:-1]
barWidth = np.min(np.diff(bins))/4
plt.figure()
plt.bar(xPdf,histOrig[0]/sum(histOrig[0])*100,barWidth)
plt.bar(xPdf + barWidth,histLang[0]/sum(histLang[0])*100, barWidth)
plt.bar(xPdf + 2* barWidth,histMarkov[0]/sum(histMarkov[0])*100, barWidth)
plt.xlabel('kW')
plt.ylabel('Percent of time [%]')
plt.legend(['Original','Langevin','Markov'])
plt.savefig('pdf  '+timeNow+'.png')
plt.show()

### rainflow
# find extremeties
def turningpoints(lst):
    dx = np.diff(lst)
    dxSign = np.sign(dx) # get the sign of the differences
    ddxSign = np.diff(dxSign) # differences of the sign of differences, indicate all turning points
    idxTurn = np.where(ddxSign)[0]
    return [lst[int(idx+1)] for idx in idxTurn]

# Take the integral of the time series. If this is a load profile, given a perfectly level power source, these cycle
# amplitudes represent the total energy in and out of the energy storage system, the total require capacity. If the
# time series is a generating profile and the load is perfectly level, it means the same thing.
langCumSum = np.cumsum(df.fixed.total_p - np.mean(df.fixed.total_p))
MarkCumSum = np.cumsum(dfMarkov.fixed.total_p - np.mean(dfMarkov.fixed.total_p))
origCumSum = np.cumsum(AHighRes.raw.total_p - np.mean(AHighRes.raw.total_p))
CumSumArray = np.concatenate((origCumSum[:len(langCumSum),np.newaxis], langCumSum[:,np.newaxis], MarkCumSum[:,np.newaxis]),1)

legendTxt = ['Original','Langevin','Markov']
plt.close('all') # close all figures
for col in range(CumSumArray.shape[1]):
    valExt = turningpoints(CumSumArray[:,col]) # get extreema of series
    rf = rainflow(np.array(valExt))
    idxRf = rf[0, :].argsort()
    rf = rf[:, idxRf]
    cycleAmp = rf[0, :]
    # ess savings are cycle amplitude (peak) * number of full cyles * 2
    # (since 1 half cycle is a charge/discharge)
    essSavings = np.cumsum(rf[0, :] * rf[3, :]) * 2
    # bin
    rfCount = np.histogram(rf, 20)
    plt.figure(0)
    plt.loglog(cycleAmp, essSavings)
    plt.xlabel('Maximum cycle amplitude [kWh]')
    plt.ylabel('Total throughput [kWh]')
    # bin values
    binsRf = np.logspace(np.log10(np.min(cycleAmp)), np.log10(np.max(cycleAmp) * 1.1), 20)
    idxBinsRf = np.digitize(cycleAmp, binsRf)  # get the indicies for the binned cycle amplitudes

    numCyclesBinned = []  # initiate the number of cycles per bin
    for idx in range(len(binsRf)):  # for each bin
        numCyclesBinned += [sum(rf[3, idxBinsRf == idx])]
    # plot
    plt.figure(1)
    plt.plot(CumSumArray[:,col])
    plt.ylabel('State of charge [kWh]')
    plt.figure(2)
    plt.loglog(binsRf, numCyclesBinned, '*-')
    plt.xlabel('Cycle Amplitude [kWh]')
    plt.ylabel('Number of cycles')
    plt.figure(3)
    plt.loglog(binsRf, numCyclesBinned * binsRf, '*-')
    plt.xlabel('Cycle Amplitude [kWh]')
    plt.ylabel('Throughput [kWh]')

# save figures
plt.figure(0)
plt.legend(legendTxt)
plt.savefig('Rainflow Cumulative throughput '+timeNow+'.png')
plt.figure(1)
plt.legend(legendTxt)
plt.savefig('Rainflow Cumulative time series '+timeNow+'.png')
plt.figure(2)
plt.legend(legendTxt)
plt.savefig('Rainflow Cycles per amplitude '+timeNow+'.png')
plt.figure(3)
plt.legend(legendTxt)
plt.savefig('Rainflow throuput per amplitude '+timeNow+'.png')

langExt = turningpoints(langCumSum)
origExt = turningpoints(origCumSum)
rf = rainflow(np.array(langExt))
# sort according to cycle amplitude
idxRf = rf[0,:].argsort()
rf = rf[:,idxRf]
cycleAmp = rf[0,:]
# ess savings are cycle amplitude (peak) * number of full cyles * 2
# (since 1 half cycle is a charge/discharge)
essSavings = np.cumsum(rf[0,:]*rf[3,:])*2
# bin
rfCount = np.histogram(rf,20)
plt.figure()
plt.loglog(cycleAmp,essSavings)
plt.xlabel('Maximum cycle amplitude [kWh]')
plt.ylabel('Total throughput [kWh]')

# TODO: bin count according to amplitude bins, to get the number of cycles and total throughput per cycle amplitude
#binsRfLang = np.concatenate(([0],0,np.log10(np.max(cycleAmp)*1.1),15))) # all cycles with amplitude less than 1, put together
binsRfLang = np.logspace(np.log10(np.min(cycleAmp)),np.log10(np.max(cycleAmp)*1.1),20)
idxBinsRfLang = np.digitize(cycleAmp, binsRfLang) # get the indicies for the binned cycle amplitudes

numCyclesBinnedLang = [] # initiate the number of cycles per bin
for idx in range(len(binsRfLang)): # for each bin
    numCyclesBinnedLang += [sum(rf[3,idxBinsRfLang == idx])]

# plot
plt.figure()
plt.plot(langCumSum)
plt.ylabel('')
plt.figure()
plt.loglog(binsRfLang, numCyclesBinnedLang,'*-')
plt.figure()
plt.loglog(binsRfLang, numCyclesBinnedLang*binsRfLang,'*-')



### statistics
def getStats(sig):
    # sig is the signal to get parameters for
    percentiles = [1,10,25,50,75,90,99]
    perctVal = []
    for percentile in percentiles:
        perctVal += [np.percentile(sig,percentile)]
    return [np.mean(sig), np.min(sig), np.max(sig), np.std(sig)], perctVal

statsOrig = getStats(AHighRes.raw.total_p)
statsLang = getStats(df.fixed.total_p)
statsMark = getStats(dfMarkov.fixed.total_p)

os.chdir(saveLocation)
import csv
with open('stats'+timeNow+'.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(statsOrig)
    spamwriter.writerow(statsLang)
    spamwriter.writerow(statsMark)

# TODO: finish
def saveFigure(extension):
    import tkinter as tk
    from tkinter import filedialog
    print('Choose the where to save the figure.')
    f = filedialog.asksaveasfile(mode='w', defaultextension=extension)
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str(text.get(1.0, END))  # starts from `1.0`, not `0.0`
    f.write(text2save)
    f.close()  # `()` was missing.



    root = tk.Tk()
    root.withdraw()
    figName = filedialog.asksaveasfile()
    plt.savefig('AutoCorrelation.png')