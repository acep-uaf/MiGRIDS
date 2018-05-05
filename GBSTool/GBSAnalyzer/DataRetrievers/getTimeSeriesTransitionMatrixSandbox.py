
from getTimeSeriesTransitionMatrix import getTransitionMatrix
import sys
import os
from readNCFile import readNCFile
from netCDF4 import Dataset
import random as rm


# load a time series
os.chdir('C:/Users/jbvandermeer/Documents/ACEP/GBS/GBSTools_0/GBSProjects/StMary/InputData/TimeSeriesData/RawData')

rootgrp = Dataset('StMaryTotalizerLoadkW.nc', "r", format="NETCDF4")
time = rootgrp.variables['time']
value = rootgrp.variables['value']

TM = getTransitionMatrix(value)

# generate test time series
start = value[0]

for idx in range(100):


print('sef')