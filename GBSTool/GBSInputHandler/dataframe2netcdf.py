# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 23, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is passed a pandas dataframe and converts it to net cdf format
def dataframe2netcdf(df,saveName,saveLocation,units,varnames=None):
    # df is the dataframe. The headers will be used as the variable names unless they are specified by the 'headers' input
    # argument
    # units are the units corresponding to the collumns in the dataframe
    # varNames are the names of the variables specified by the columns of the dataframe
    # TODO: the data type of df needs to be numerical (or not object)
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

    rootgrp = Dataset(saveName,'w',format='NETCDF4')
    rootgrp.createDimension('dim', None) # create dimension for all variables
    import pandas as pd
    for i in range(df.shape[1]):
        # header name from data frame
        column = df.columns.values[i]
        if varnames != None:
            rootgrp.createVariable(varnames[i], df.dtypes[i],'dim')  # create a var using the varnames
            rootgrp.variables[varnames[i]][:] = np.array(df[column]) # fill with values
        else:
            rootgrp.createVariable(column, df.dtypes[i],'dim')  # create a var using the header from the df for var name
            rootgrp.variables[column][:] = np.array(df[column]) # fill with values
        rootgrp.variables[column].units = units[i] # set unit attribute





    # end of file
    return rootgrp




# test implementation
# create a dataframe
# from pandas import DataFrame
# df = DataFrame([(1,2,3),(2,2,2),(3,3,3)],columns=['a','b','c'])
# ncData = dataframe2netcdf(df,'test.nc',['kW','kvar','kPA'])
# print(ncData.variables))