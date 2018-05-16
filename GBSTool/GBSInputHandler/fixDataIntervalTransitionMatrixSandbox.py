
from fixDataIntervalTransitionMatrix import fixDataIntervalTransitionMatrix
from fixDataInterval import fixDataInterval
from fixBadData import DataClass
import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
import datetime
import scipy.fftpack
import copy
import os
from netCDF4 import Dataset

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

#### grab Igiugig data ####
# cd to Igiugig data
here = os.path.dirname(os.path.realpath(__file__))
os.chdir(here)
os.chdir('..\..\GBSProjects\Igiugig0\InputData\TimeSeriesData\ProcessedData')
# totalizer load, 15 min averages
rootgrp = Dataset('load0P.nc', "r", format="NETCDF4")
date_list = pd.to_datetime(rootgrp.variables['time'][0],unit='s')
values = rootgrp.variables['value'][0]

# Reduce the size of data to speed up testing
N = 10000 # sample size
date_list = date_list[:N]
values = values[:N]

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
'''
### test Langevin upsampling ###
df = fixDataIntervalTransitionMatrix(A,'1s','','')
plt.plot(df.fixed.gen1,'*-')
plt.plot(df.raw.gen1,'*-')
plt.show()

# test frequency distribution
# get the fft of input data
yf_in = scipy.fftpack.fft(values)
N_in = len(t)
xf_in = np.linspace(0.0, 0.5*Fs, int(N_in/2))
# get fft of output data
yf_out = scipy.fftpack.fft(df.fixed.gen1)
N_out = len(df.fixed.gen1)
xf_out = np.linspace(0.0, 0.5*1, int(N_out/2))

# plot fft
plt.figure()
plt.plot(xf_in, 2.0/N_in * np.abs(yf_in[:int(N_in/2)]))
plt.plot(xf_out, 2.0/N_out * np.abs(yf_out[:int(N_out/2)]))

plt.show()
'''
### Test Markov ###

# get transition matrix of differences from the moving average
from GBSAnalyzer.DataRetrievers.getTimeSeriesTransitionMatrix import getTransitionMatrix
window = TsRatio # make the window size the number of steps inbetween the low res data steps
valuesMovAve = AHighRes.raw.total_p.rolling(window).mean()
valuesMovAve = valuesMovAve.bfill()
valuesDiff = AHighRes.raw.total_p - valuesMovAve
tm, tmValues = getTransitionMatrix(valuesDiff,numStates=100)

dfMarkov = fixDataIntervalTransitionMatrix(Acopy,'1s', True, tm, tmValues)

plt.figure()
plt.plot(dfMarkov.fixed.total_p,'*-')
#plt.plot(df.fixed.gen1,'*-')
plt.plot(dfMarkov.raw.total_p,'*-')
plt.show()

# test frequency distribution
# get fft of output data
yf_outMarkov = scipy.fftpack.fft(dfMarkov.fixed.gen1)
N_outMarkov = len(dfMarkov.fixed.gen1)
xf_outMarkov = np.linspace(0.0, 0.5*1, int(N_out/2))