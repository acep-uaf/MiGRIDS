

import sys
import os
from readNCFile import readNCFile
from netCDF4 import Dataset
import matplotlib.pyplot as plt
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
from getTimeSeriesTransitionMatrix import getTransitionMatrix
from CurveAssemblers.generateTimeSeriesFromTransitionMatrix import generateTimeSeries

# load a time series
os.chdir('C:/Users/jbvandermeer/Documents/ACEP/GBS/GBSTools_0/GBSProjects/StMary/InputData/TimeSeriesData/RawData')

# totalizer load, 15 min averages
rootgrp = Dataset('StMaryTotalizerLoadkW.nc', "r", format="NETCDF4")
time = rootgrp.variables['time']
value = rootgrp.variables['value']

# train on totalizer load for now, in future train on fast data after cleaned.
TM, bins = getTransitionMatrix(value[0])

# generate a time series
T = 15*60 # sampling period in seconds
startingIdx = round(len(bins)/2)
length = 100000
ts = generateTimeSeries(TM, bins, startingIdx, length)

# plot the time series
plt.figure()
plt.plot(ts)
plt.show()

print('sef')