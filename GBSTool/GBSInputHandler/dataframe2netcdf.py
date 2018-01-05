# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 23, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is passed a pandas dataframe and converts it to net cdf format
def dataframe2netcdf(df,units,scale,offset,varnames=None,saveLocation=''):
    # df is the dataframe. The headers will be used as the variable names unless they are specified by the 'headers' input
    # argument
    # units are the units corresponding to the collumns in the dataframe, *type string*
    # scale and offset correspond to the data collumns *type float*
    # varNames are the names of the variables specified by the columns of the dataframe *type string*
    # saveLocation is where the net CDF files are saved *type string*

    # general imports
    from netCDF4 import Dataset
    import numpy as np
    from tkinter import filedialog
    import os

    # go to save directory
    if saveLocation == '':
        print('Choose directory where to save the netCDF file.')
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        saveLocation = filedialog.askdirectory()
    os.chdir(saveLocation)

    # create a netCDF file for each data column of the data frame containing the timestamps and the data
    for i in range(1,df.shape[1]): # skip the first column, Date
        # get header name from data frame
        column = df.columns.values[i]
        if varnames != None:
            ncName = varnames[i-1] + '.nc'
        else:
            ncName = column + '.nc'
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




    # end of file


