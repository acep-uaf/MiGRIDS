# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# get input data to run the functions to import data into the project
from tkinter import filedialog
import tkinter as tk
import os
from GBSAnalyzer.DataRetrievers.readXmlTag import readXmlTag
from GBSInputHandler.getUnits import getUnits

from GBSInputHandler.mergeInputs import mergeInputs



#print('Select the xml project setup file')
root = tk.Tk()
root.withdraw()
root.attributes('-topmost',1)
fileName = filedialog.askopenfilename()
# get the setup Directory

setupDir = os.path.dirname(fileName)
# Village name

Village = readXmlTag(fileName,'project','name')[0]
# input specification
#input specification can be for multiple input files or a single file in AVEC format.
inputSpecification = readXmlTag(fileName,'inputFileFormat','value')
inputDictionary = {}
#filelocation is the raw timeseries file.
#if multiple files specified look for raw_wind directory
# input a list of subdirectories under the GBSProjects directory
fileLocation = readXmlTag(fileName,'inputFileDir','value')
inputDictionary['fileLocation'] = [os.path.join('../GBSProjects', *x) for x in fileLocation]
# file type
inputDictionary['fileType'] = readXmlTag(fileName,'inputFileType','value')



inputDictionary['outputInterval'] = readXmlTag(fileName,'timeStep','value')
inputDictionary['outputIntervalUnit'] = readXmlTag(fileName,'timeStep','unit')
inputDictionary['inputInterval'] = readXmlTag(fileName,'inputTimeStep','value')
inputDictionary['inputIntervalUnit'] = readXmlTag(fileName,'inputTimeStep','unit')

# get date and time values
inputDictionary['dateColumnName'] = readXmlTag(fileName,'dateChannel','value')
inputDictionary['dateColumnFormat'] = readXmlTag(fileName,'dateChannel','format')
inputDictionary['timeColumnName'] = readXmlTag(fileName,'timeChannel','value')
inputDictionary['timeColumnFormat'] = readXmlTag(fileName,'timeChannel','format')
inputDictionary['utcOffsetValue'] = readXmlTag(fileName,'inputUTCOffset','value')
inputDictionary['utcOffsetUnit'] = readXmlTag(fileName,'inputUTCOffset','unit')
inputDictionary['dst'] = readXmlTag(fileName,'inputDST','value')
flexibleYear = readXmlTag(fileName,'flexibleYear','value')
# convert string to bool
inputDictionary['flexibleYear'] = [(x.lower() == 'true') | (x.lower() == 't') for x in flexibleYear]
#HOW is a list for outputIntervals handled downstream - should this code ensure there is only one value moving forward instead of creating a list
#THIS NEEDS TO MOVE TO A FUNCTION. UI does not call runDataImport
for idx in range(len(inputDictionary['outputInterval'])): # there should only be one output interval specified
    if len(inputDictionary['outputInterval']) > 1:
        inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][idx]
    else:
        inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][0]

for idx in range(len(inputDictionary['inputInterval'])):  # for each group of input files
    if len(inputDictionary['inputIntervalUnit']) > 1:
        inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][idx]
    else:
        inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][0]


# get data units and header names
inputDictionary['headerNames'], inputDictionary['componentUnits'], inputDictionary['componentAttributes'],inputDictionary['componentNames'], inputDictionary['newHeaderNames'] = getUnits(Village,setupDir)

# read time series data, combine with wind data if files are seperate.
df, listOfComponents = mergeInputs(inputDictionary)

# now fix the bad data
from fixBadData import fixBadData
df_fixed = fixBadData(df,setupDir,listOfComponents,inputDictionary['inputInterval'])

# check the fixed data with the old data
# plot data, display statistical differences (min, max, mean std difference etc)

# fix the intervals
from fixDataInterval import fixDataInterval
df_fixed_interval = fixDataInterval(df_fixed,inputDictionary['outputInterval'])

d = {}
for c in listOfComponents:
    d[c.component_name] = c.toDictionary()
# now convert to a netcdf
from dataframe2netcdf import dataframe2netcdf
dataframe2netcdf(df_fixed_interval.fixed, d)
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/
