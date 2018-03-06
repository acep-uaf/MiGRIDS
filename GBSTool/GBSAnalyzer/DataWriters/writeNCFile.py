
# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 21, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
from netCDF4 import Dataset

def writeNCFile(time_epoch,value,Scale,Offset,Units,SaveName):
    rootgrp = Dataset(SaveName, 'w', format='NETCDF4')  # create netCDF object
    rootgrp.createDimension('time', None)  # create dimension for all called time
    # create the time variable
    rootgrp.createVariable('time', type(time_epoch[0]), 'time')  # create a var using the varnames
    rootgrp.variables['time'][:] = time_epoch  # fill with values
    # create the value variable
    rootgrp.createVariable('value', type(value[0]), 'time')  # create a var using the varnames
    rootgrp.variables['value'][:] = value  # fill with values
    # assign attributes
    rootgrp.variables['time'].units = 'seconds'  # set unit attribute
    rootgrp.variables['value'].units = Units  # set unit attribute
    rootgrp.variables['value'].Scale = Scale  # set unit attribute
    rootgrp.variables['value'].offset = Offset  # set unit attribute
    # close file
    rootgrp.close()