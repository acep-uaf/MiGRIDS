# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# get input data to run the functions to import data into the project
#from tkinter import filedialog
#import tkinter as tk
import os

from GBSInputHandler.getUnits import getUnits
from GBSInputHandler.fixBadData import fixBadData
from GBSInputHandler.fixDataInterval import fixDataInterval
from GBSInputHandler.dataframe2netcdf import dataframe2netcdf
from GBSInputHandler.mergeInputs import mergeInputs
from GBSController.UIToHandler import UIToHandler
from GBSInputHandler.readSetupFile import readSetupFile
import pickle

#root = tk.Tk()
#root.withdraw()
#root.attributes('-topmost',1)
#fileName = filedialog.askopenfilename()

#specify the correct path to your project setup file here
fileName = os.path.join(os.getcwd(),*['..\\' 'GBSProjects','SampleProject','InputData','Setup','SampleProjectSetup.xml'])
# get the setup Directory
setupDir = os.path.dirname(fileName)
inputDictionary = readSetupFile(fileName)
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
os.chdir(setupDir)
inFile = open("df_raw.pkl", "rb")
df= pickle.load(inFile)
inFile.close()
inFile = open("component.pkl", "rb")
listOfComponents = pickle.load(inFile)
inFile.close()

#fix missing or bad data
df_fixed = fixBadData(df, setupDir,listOfComponents,inputDictionary['runTimeSteps'])
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

