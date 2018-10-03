# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 23, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is passed a pandas dataframe and converts it to net cdf format
def dataframe2netcdf(df,components,saveLocation=''):
    # df is the dataframe. The headers will be used as the variable names unless they are specified by the 'headers' input
    # components is a dictionary of units and offsets for each component
    # varNames are the names of the variables specified by the columns of the dataframe *type string*
    # saveLocation is where the net CDF files are saved *type string*

    # general imports
    from netCDF4 import Dataset
    import numpy as np
    from tkinter import filedialog
    import os

    # go to save directory
    here = os.getcwd()
    if saveLocation == '':
        print('Choose directory where to save the netCDF file.')
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', 1)
        saveLocation = filedialog.askdirectory()
    os.chdir(saveLocation)
    netCDFList = []
    # create a netCDF file for each data column of the data frame containing the timestamps and the data
    for component in components.keys():
        # get header name from dataframe
        try:
            column = [c for c,x in enumerate(df.columns.values) if x == component]
            if len(column) >0:
                column = column[0]
            ncName = component + '.nc'
            rootgrp = Dataset(ncName, 'w', format='NETCDF4') # create netCDF object
            rootgrp.createDimension('time', None)  # create dimension for all called time
            # create the time variable
            rootgrp.createVariable('time', df.dtypes[column], 'time')  # create a var using the varnames
            rootgrp.variables['time'][:] = np.array(df.index.astype(np.int64)//10**9)  # fill with values
            # create the value variable
            rootgrp.createVariable('value', df.dtypes[column], 'time')  # create a var using the varnames
            rootgrp.variables['value'][:] = np.array(df[component])  # fill with values
            # assign attributes
            rootgrp.variables['time'].units = 'seconds'  # set unit attribute
            rootgrp.variables['value'].units = components[component]['units'] # set unit attribute
            rootgrp.variables['value'].Scale = components[component]['scale'] # set unit attribute
            rootgrp.variables['value'].offset = components[component]['offset']  # set unit attribute
            # close file
            rootgrp.close()
            netCDFList.append(component)
        except:
            #if a netcdf file wasn't created successfully, move on to the next one
            continue
    # return to the starting directory
    os.chdir(here)
    return netCDFList

