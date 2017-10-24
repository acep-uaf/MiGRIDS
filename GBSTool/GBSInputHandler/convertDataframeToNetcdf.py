# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 23, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is passed a pandas dataframe and converts it to net cdf format
def convertDataframeToNetcdf(df,saveName,units,varNames):
    # df is the dataframe. The headers will be used as the variable names unless they are specified by the 'headers' input
    # argument
    # units are the units corresponding to the collumns in the dataframe
    # varNames are the names of the variables specified by the columns of the dataframe

    from netCDF4 import Dataset
    rootgrp = Dataset(saveName,'w',format='NETCDF4')
    import pandas as pd
    for column in df:
        rootgrp.createGroup(df.columns.values[column])



    # end of file
    rootgrp.close()
