# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# get input data to run the functions to import data into the project
from tkinter import filedialog
import tkinter as tk
#print('Select the xml project setup file')
root = tk.Tk()
root.withdraw()
root.attributes('-topmost',1)
fileName = filedialog.askopenfilename()
# get the setup Directory
import os
setupDir = os.path.dirname(fileName)
# Village name
from readXmlTag import readXmlTag
Village = readXmlTag(fileName,'project','name')[0]
# input specification
inputSpecification = readXmlTag(fileName,'inputFileFormat','value')[0]
# input a list of subdirectories under the GBSProjects directory
fileLocation = readXmlTag(fileName,'inputFileDir','value')
fileLocation = os.path.join(*fileLocation)
fileLocation = os.path.join('../../GBSProjects', fileLocation)
# file type
fileType = readXmlTag(fileName,'inputFileType','value')[0]
outputInterval = readXmlTag(fileName,'outputTimeStep','value')[0] + readXmlTag(fileName,'outputTimeStep','unit')[0]
inputInterval = readXmlTag(fileName,'inputTimeStep','value')[0] + readXmlTag(fileName,'inputTimeStep','unit')[0]

# get data units and header names
from getUnits import getUnits
headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames = getUnits(Village,setupDir)

# read time series data
from readDataFile import readDataFile
df, listOfComponents= readDataFile(inputSpecification,fileLocation,fileType,headerNames,newHeaderNames,componentUnits,componentAttributes) # dataframe with time series information. replace header names with column names

# now fix the bad data
from fixBadData import fixBadData
df_fixed = fixBadData(df,setupDir,listOfComponents,inputInterval)

# check the fixed data with the old data
# plot data, display statistical differences (min, max, mean std difference etc)

# fix the intervals
from fixDataInterval import fixDataInterval
df_fixed_interval = fixDataInterval(df_fixed,outputInterval)


# now convert to a netcdf
from dataframe2netcdf import dataframe2netcdf
dataframe2netcdf(df_fixed_interval.fixed, listOfComponents)
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/
