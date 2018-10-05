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
from GBSInputHandler.fixBadData import fixBadData
from GBSInputHandler.fixDataInterval import fixDataInterval
from GBSInputHandler.dataframe2netcdf import dataframe2netcdf
from GBSInputHandler.mergeInputs import mergeInputs
import pickle

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
inputDictionary['runTimeSteps'] = readXmlTag(fileName,'runTimeSteps','value')
#inputDictionary['inputInterval'] = readXmlTag(fileName,'inputTimeStep','value')
#inputDictionary['inputIntervalUnit'] = readXmlTag(fileName,'inputTimeStep','unit')

# get date and time values
inputDictionary['dateColumnName'] = readXmlTag(fileName,'dateChannel','value')
inputDictionary['dateColumnFormat'] = readXmlTag(fileName,'dateChannel','format')
inputDictionary['timeColumnName'] = readXmlTag(fileName,'timeChannel','value')
inputDictionary['timeColumnFormat'] = readXmlTag(fileName,'timeChannel','format')
inputDictionary['utcOffsetValue'] = readXmlTag(fileName,'inputUTCOffset','value')
inputDictionary['utcOffsetUnit'] = readXmlTag(fileName,'inputUTCOffset','unit')
inputDictionary['dst'] = readXmlTag(fileName,'inputDST','value')
inputDictionary['timeZone'] = readXmlTag(fileName,'timeZone','value')

flexibleYear = readXmlTag(fileName,'flexibleYear','value')

# convert string to bool
inputDictionary['flexibleYear'] = [(x.lower() == 'true') | (x.lower() == 't') for x in flexibleYear]

for idx in range(len(inputDictionary['outputInterval'])): # there should only be one output interval specified
    if len(inputDictionary['outputInterval']) > 1:
        inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][idx]
    else:
        inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][0]

#for idx in range(len(inputDictionary['inputInterval'])):  # for each group of input files
#    if len(inputDictionary['inputIntervalUnit']) > 1:
#        inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][idx]
#    else:
#        inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][0]

# get data units and header names
inputDictionary['columnNames'], inputDictionary['componentUnits'], \
inputDictionary['componentAttributes'],inputDictionary['componentNames'], inputDictionary['useNames'] = getUnits(Village,setupDir)

print(inputDictionary)
# read time series data, combine with wind data if files are seperate.
df, listOfComponents = mergeInputs(inputDictionary)

#view the resulting dataframe
print(df.head())

#save the dataframe and components used
#its recommended that you save the data at each stage since the process can be time consuming to repeat.
os.chdir(setupDir)
out = open("df_raw.pkl","wb")
pickle.dump(df,out )
out.close()
out = open("component.pkl","wb")
pickle.dump(listOfComponents,out)
out.close()

#IF YOU ARE STARTING FROM AN EXISTING DF and COMPONENTS USE THE CODE BELOW TO LOAD
# os.chdir(setupDir)
# inFile = open("df_fixed.p", "rb")
# df_fixed = pickle.load(inFile)
# inFile.close()
# inFile = open("component.pkl", "rb")
# listOfComponents = pickle.load(inFile)
# inFile.close()

#fix missing or bad data
df_fixed = fixBadData(setupDir,listOfComponents,inputDictionary['runTimeSteps'])
# fix the intervals
df_fixed_interval = fixDataInterval(df_fixed,inputDictionary['outputInterval'])

# pickle df
os.chdir(setupDir)
pickle.dump(df_fixed_interval, open("df_fixed_interval.p","wb"))

d = {}
for c in listOfComponents:
    d[c.column_name] = c.toDictionary()

# now convert to a netcdf
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/Processed'''
dataframe2netcdf(df_fixed_interval.fixed, d)

