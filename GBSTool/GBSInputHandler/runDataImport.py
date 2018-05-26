# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# get input data to run the functions to import data into the project
from tkinter import filedialog
import tkinter as tk
import pandas as pd
#print('Select the xml project setup file')
root = tk.Tk()
root.withdraw()
root.attributes('-topmost',1)
fileName = filedialog.askopenfilename()
# get the setup Directory
import os
setupDir = os.path.dirname(fileName)
# Village name
from GBSAnalyzer.DataRetrievers.readXmlTag import readXmlTag
Village = readXmlTag(fileName,'project','name')[0]
# input specification
#input specification can be for multiple input files or a single file in AVEC format.
inputSpecification = readXmlTag(fileName,'inputFileFormat','value')
#filelocation is the raw timeseries file.
#if multiple files specified look for raw_wind directory
# input a list of subdirectories under the GBSProjects directory
fileLocation = readXmlTag(fileName,'inputFileDir','value')
fileLocation = [os.path.join('../../GBSProjects', *x) for x in fileLocation]
# file type
fileType = readXmlTag(fileName,'inputFileType','value')

outputInterval = readXmlTag(fileName,'timeStep','value')
outputIntervalUnit = readXmlTag(fileName,'timeStep','unit')
inputInterval = readXmlTag(fileName,'inputTimeStep','value')
inputIntervalUnit = readXmlTag(fileName,'inputTimeStep','unit')

# get date and time values
dateColumnName = readXmlTag(fileName,'dateChannel','value')
dateColumnFormat = readXmlTag(fileName,'dateChannel','format')
timeColumnName = readXmlTag(fileName,'timeChannel','value')
timeColumnFormat = readXmlTag(fileName,'timeChannel','format')
utcOffsetValue = readXmlTag(fileName,'inputUTCOffset','value')
utcOffsetUnit = readXmlTag(fileName,'inputUTCOffset','unit')
dst = readXmlTag(fileName,'inputDST','value')

for idx in range(len(outputInterval)): # for each group of input files
    if len(outputIntervalUnit) > 1:
        outputInterval[idx] += outputIntervalUnit[idx]
    else:
        outputInterval[idx] += outputIntervalUnit[0]
    if len(inputIntervalUnit) > 1:
        inputInterval[idx] += inputIntervalUnit[idx]
    else:
        inputInterval[idx] += inputIntervalUnit[0]


# get data units and header names
from getUnits import getUnits
headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames = getUnits(Village,setupDir)

# read time series data, combine with wind data if files are seperate.
from readDataFile import readDataFile
# iterate through all sets of input files
for idx in range(len(fileLocation)):
    df0, listOfComponents0= readDataFile(fileType[idx],fileLocation[idx],fileType[idx],headerNames[idx],newHeaderNames[idx],componentUnits[idx],componentAttributes[idx], dateColumnName[idx], dateColumnFormat[idx], timeColumnName[idx], timeColumnFormat[idx], utcOffsetValue[idx], utcOffsetUnit[0], dst[idx]) # dataframe with time series information. replace header names with column names
    if idx == 0: # initiate data frames if first iteration, otherwise append
        df = df0
        listOfComponents = listOfComponents0
    else:
        df = pd.merge(df,df0,how='outer',on='DATE')
        listOfComponents.append(listOfComponents0)
# now fix the bad data
from fixBadData import fixBadData
df_fixed = fixBadData(df,setupDir,listOfComponents,inputInterval)

# check the fixed data with the old data
# plot data, display statistical differences (min, max, mean std difference etc)

# fix the intervals
from fixDataInterval import fixDataInterval
df_fixed_interval = fixDataInterval(df_fixed,outputInterval)

d = {}
for c in listOfComponents:
    d[c.component_name] = c.toDictionary()
# now convert to a netcdf
from dataframe2netcdf import dataframe2netcdf
dataframe2netcdf(df_fixed_interval.fixed, d)
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/
