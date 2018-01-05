# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# get input data to run the functions to import data into the project
from tkinter import filedialog
import tkinter as tk
print('Select the xml project setup file.')
root = tk.Tk()
root.withdraw()
fileName = filedialog.askopenfilename()
# get the setup Directory
import os
setupDir = os.path.dirname(fileName)
# Village name
from readXmlTag import readXmlTag
Village = readXmlTag(fileName,'project','name')[0]
# input specification
inputSpecification = readXmlTag(fileName,'inputFileFormat','value')[0]
# input time series data files location
fileLocation = readXmlTag(fileName,'inputFileDir','value')[0]
# file type
fileType = readXmlTag(fileName,'inputFileType','value')[0]
interval = readXmlTag(fileName,'timeStep','value')[0] + readXmlTag(fileName,'timeStep','unit')[0]

'''
# input data
Village = 'Chevak'
setupDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools1\GBSProjects\Chevak\InputData\Setup'
inputSpecification = 'AVEC'
fileLocation = ''
fileType = '.CSV'
columnNames = None
interval = '30s' # the desired number of seconds between data points. This needs to be pulled from a file, not set here
'''

# get data units and header names
from getUnits import getUnits
headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames = getUnits(Village,setupDir)

# read time series data
from readDataFile import readDataFile
df, units, scale, offset = readDataFile(inputSpecification,fileLocation,fileType,headerNames,newHeaderNames,componentUnits,componentAttributes) # dataframe with time series information. replace header names with column names

# now fix the bad data
from fixBadData import fixBadData
df_fixed = fixBadData(df,setupDir,componentNames)

# check the fixed data with the old data
# plot data, display statistical differences (min, max, mean std difference etc)

# fix the intervals
from fixDataInterval import fixDataInterval
df_fixed_interval = fixDataInterval(df_fixed,interval)

# now convert to a netcdf
from dataframe2netcdf import dataframe2netcdf
dataframe2netcdf(df_fixed_interval,units,scale,offset)
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/
