
from netCDF4 import Dataset
import numpy as np
import os

# create a nc file for load
rootgrp = Dataset(ncName, 'w', format='NETCDF4') # create netCDF object
rootgrp.createDimension('time', None)  # create dimension for all called time
# create the time variable
rootgrp.createVariable('time', df.dtypes[i], 'time')  # create a var using the varnames
rootgrp.variables['time'][:] = np.array(df[df.columns.values[0]])  # fill with values
# create the value variable
rootgrp.createVariable('value', df.dtypes[i], 'time')  # create a var using the varnames
rootgrp.variables['value'][:] = np.array(df[column])  # fill with values
# assign attributes
rootgrp.variables['time'].units = 'seconds'  # set unit attribute
rootgrp.variables['value'].units = units[i-1] # set unit attribute
rootgrp.variables['value'].Scale = scale[i - 1]  # set unit attribute
rootgrp.variables['value'].offset = offset[i - 1]  # set unit attribute
# close file
rootgrp.close()