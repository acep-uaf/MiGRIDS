# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# input data
Village = 'Chevak'
setupDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools1\GBSProjects\Chevak\InputData\Setup'
inputSpecification = 'AVEC'
fileLocation = ''
fileType = '.CSV'
columnNames = None
interval = 1 # the desired number of seconds between data points. This needs to be pulled from a file, not set here

# get data units and header names
from getUnits import getUnits
headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames = getUnits(Village,setupDir)

# read time series data
from readDataFile import readDataFile
df = readDataFile(inputSpecification,fileLocation,fileType,headerNames,newHeaderNames,componentUnits) # dataframe with time series information. replace header names with column names

# now fix the bad data
from fixBadData import fixBadData
(df_fixed,badInd) = fixBadData(df,setupDir,projectName)

# check the fixed data with the old data
# plot data, display statistical differences (min, max, mean std difference etc)

# fix the intervals
# TODO: Figure out where we get the desired interval from. There should be a general setup file somewhere.
from fixDataInterval import fixDataInterval
df_fixed_interval = fixDataInterval(df_fixed,interval)

# now convert to a netcdf
# TODO: create general setup file wtih Village name

# now convert to a netcdf
# TODO: create general setup file wtih Village name
from dataframe2netcdf import dataframe2netcdf
ncfile = dataframe2netcdf(df_fixed_interval,projectName+'Data.nc','',componentUnits)
print(ncfile.variables)
ncfile.close()
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/