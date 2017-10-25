# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def getComponentDescriptor(varNames):
    # varNames are the variable names (corresponding to component descriptor file names) to generate a netcdf with

    # temporary fix

    from netCDF4 import Dataset
    ncfile = Dataset('test.nc', 'w', format='NETCDF4')


    return ncfile

