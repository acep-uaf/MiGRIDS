# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 23, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is passed a pandas dataframe and converts it to net cdf format
def dataframe2netcdf(df,saveName,units,varnames=None):
    # df is the dataframe. The headers will be used as the variable names unless they are specified by the 'headers' input
    # argument
    # units are the units corresponding to the collumns in the dataframe
    # varNames are the names of the variables specified by the columns of the dataframe
    from netCDF4 import Dataset
    rootgrp = Dataset(saveName,'w',format='NETCDF4')
    import pandas as pd
    for i in range(len(df)):
        column = df.columns.values[i]
        rootgrp.createDimension(column, None) # create a dimension for the variable
        if varnames != None:
            rootgrp.createVariable(varnames, df.dtypes[i],
                                   (column,))  # create a var using the varnames from the df for var name
        else:
            rootgrp.createVariable(column, df.dtypes[i],
                                   (column,))  # create a var using the header from the df for var name
        rootgrp['/'+column].units = units[i] # set unit property





    # end of file
    return rootgrp




# test implementation
# create a dataframe
from pandas import DataFrame
df = DataFrame([(1,2,3),(2,2,2),(3,3,3)],columns=['a','b','c'])
ncData = convertDataframeToNetcdf(df,'test.nc',['kW','kvar','kPA'])
print(ncData.variables)