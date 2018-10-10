# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 23, 2017
# License: MIT License (see LICENSE file of this package for more information)

# Converts a pandas.DataFrame to netcdf files
def dataframe2netcdf(df,components,saveLocation=''):
    '''
    :param df: [pandas.DataFrame] a dataframe with datetime index and columns with column names that match the provided components
    :param components: [ListOf Components] a dictionary of component information. A netcdf file will be generated for each key.
    :param saveLocation: [string] directory to save netcdf files to
    :return: netCDFList [ListOf String] a list of netcdf files that were created
    '''

    # general imports
    from netCDF4 import Dataset
    import numpy as np
    from tkinter import filedialog
    import os

    # go to save directory
    here = os.getcwd()
    if saveLocation == '':
        print('savelocation not specified')
        return
    os.chdir(saveLocation)
        
    netCDFList = []
    def get(attr,default):
        if attr is None:
            return default
        return attr
    # create a netCDF file for each data column of the data frame containing the timestamps and the data
    for component in components.keys():
        # get header name from dataframe
        try:
            column = [c for c,x in enumerate(df.columns.values) if x == components[component]['column_name']]
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
            rootgrp.variables['value'].Scale = get(components[component]['scale'],1) # set unit attribute
            rootgrp.variables['value'].offset = get(components[component]['offset'],0)  # set unit attribute
            # close file
            rootgrp.close()
            netCDFList.append(ncName)
        except Exception as e:
            print('could not generate netcdf file for %s' %component)
            print(e)

            #if a netcdf file wasn't created successfully, move on to the next one
            continue
    # return to the starting directory
    os.chdir(here)
    return netCDFList

