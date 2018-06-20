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
#from GBSInputHandler.fixBadData import fixBadData
from GBSInputHandler.fixDataInterval import fixDataInterval
from GBSInputHandler.dataframe2netcdf import dataframe2netcdf
from GBSInputHandler.mergeInputs import mergeInputs
import pandas as pd
from GBSInputHandler.DataClass import DataClass
import sys

import pickle
import matplotlib.pyplot as plt

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
inputDictionary['fileLocation'] = [os.path.join('../../GBSProjects', *x) for x in fileLocation]
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
inputDictionary['headerNames'], inputDictionary['componentUnits'], \
inputDictionary['componentAttributes'],inputDictionary['componentNames'], inputDictionary['newHeaderNames'] = getUnits(Village,setupDir)

# read time series data, combine with wind data if files are seperate.
#df, listOfComponents = mergeInputs(inputDictionary)

# TODO: read from pickle for testing purposes
os.chdir(setupDir)
os.chdir('../TimeSeriesData/RawData')
inFile = open("raw_df.pkl","rb")
df = pickle.load(open("raw_df.pkl","rb"))
inFile.close()

os.chdir(setupDir)
out = open("df_raw.pkl","wb")
pickle.dump(df,out )
out.close()
out = open("component.pkl","wb")
pickle.dump(listOfComponents,out)
out.close()


# TODO: this replaces the fixBadData until it is ready
# create DataClass object to store raw, fixed, and summery outputs
# use the largest sample interval for the data class
 sampleIntervalTimeDelta = [pd.to_timedelta(s) for s in inputDictionary['inputInterval']]
df_fixed = DataClass(df, max(sampleIntervalTimeDelta))
df_fixed.eColumns = ['wtg0WS']
df_fixed.loads = ['load0P','load1P']
df_fixed.powerComponents = []
df_fixed.totalPower()
df_fixed.fixed[0].load0P[df_fixed.fixed[0].load0P<0] = None

# now fix the bad data
#df_fixed = fixBadData(df,setupDir,listOfComponents,inputDictionary['inputInterval'])

# pickle df
os.chdir(setupDir)
pickle.dump(df_fixed, open("df_fixed.p","wb"))



# fix the intervals
df_fixed_interval = fixDataInterval(df_fixed,inputDictionary['outputInterval'])

# pickle df
os.chdir(setupDir)
pickle.dump(df_fixed_interval, open("df_fixed_interval.p","wb"))

d = {}
for c in listOfComponents:
    d[c.component_name] = c.toDictionary()
# now convert to a netcdf

dataframe2netcdf(df_fixed_interval.fixed, d)
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/
