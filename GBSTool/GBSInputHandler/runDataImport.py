# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py)

# first the data is read according to certain paramters or a specifically written script.
# TODO: create general setup file or GUI with this input information
# temporary fix
inputSpecification = 'AVEC'
fileLocation = ''
fileType = '.CSV'
columnNames = None
from readDataFile import readDataFile
df = readDataFile(inputSpecification,fileLocation,fileType,columnNames)

# this returns a netcdf file with meta data corresponding to the df column headers
# TODO: possibly prompt the user to create a component descriptor(s) for data channels that dont have one
from getComponentDescriptor import getComponentDescriptor
ncParameters = getComponentDescriptor(df.columns)

# now fix the bad data
from fixBadData import fixBadData
(df_fixed,badInd) = fixBadData(df,ncParameters)

# check the fixed data with the old data
# plot data, display statistical differences (min, max, mean std difference etc)

# fix the intervals
# TODO: Figure out where we get the desired interval from. There should be a general setup file somewhere.
interval = 1 # the desired number of seconds between data points. This needs to be pulled from a file, not set here
from fixDataInterval import fixDataInterval
df_fixed_interval = fixDataInterval(df_fixed,interval)

# now convert to a netcdf
# TODO: create general setup file wtih Village name
Village = 'Chevak'
from dataframe2netcdf import dataframe2netcdf
ncfile = dataframe2netcdf(df_fixed_interval,Village,ncParameters)

# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/