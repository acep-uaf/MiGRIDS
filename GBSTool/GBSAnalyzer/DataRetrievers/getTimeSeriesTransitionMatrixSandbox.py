

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

rootgrp = Dataset('StMaryTotalizerLoadkW.nc', "r", format="NETCDF4")
time = rootgrp.variables['time']
value = rootgrp.variables['value']

TM, bins = getTransitionMatrix(value)

# generate a time series
startingIdx = round(len(bins)/2)
length = 100000
ts = generateTimeSeries(TM, bins, startingIdx, length)

# plot the time series
plt.figure()
plt.plot(ts)
plt.show()

print('sef')