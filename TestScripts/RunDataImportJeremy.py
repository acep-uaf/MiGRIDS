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
from GBSInputHandler.adjustColumnYear import adjustColumnYear

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
print(inputDictionary)
# read time series data, combine with wind data if files are seperate.
#df, listOfComponents = mergeInputs(inputDictionary)

# TODO: read from pickle for testing purposes
os.chdir(setupDir)
os.chdir('../TimeSeriesData/RawData')
inFile = open("raw_df.pkl","rb")
df = pickle.load(open("raw_df.pkl","rb"))
inFile.close()
'''
os.chdir(setupDir)
out = open("df_raw.pkl","wb")
pickle.dump(df,out )
out.close()
out = open("component.pkl","wb")
pickle.dump(listOfComponents,out)
out.close()
'''

# TODO: this replaces the fixBadData until it is ready
# create DataClass object to store raw, fixed, and summery outputs
# use the largest sample interval for the data class
sampleIntervalTimeDelta = [pd.to_timedelta(s) for s in inputDictionary['inputInterval']]
df_fixed = DataClass(df, max(sampleIntervalTimeDelta))
df_fixed.eColumns = ['wtg0WS']
df_fixed.loads = ['load0P','load1P']
df_fixed.powerComponents = []
df_fixed.totalPower()
df_fixed.fixed[0].load0P[df_fixed.fixed[0].load0P<200] = None
df_fixed.fixed[0].load0P[df_fixed.fixed[0].load0P>1000] = None
# adjust the column yearsrunDataImport.py
df_fixed.fixed[0] = adjustColumnYear(df_fixed.fixed[0])
# only take year the year 2014 from load0P
load0P0 = df_fixed.fixed[0][['load0P']].copy()
load0P1 = df_fixed.fixed[0][['load0P']].copy()
# remove not in 2014 and not early months
load0P0.load0P[(load0P0.index.year != 2014) | [x not in [1,2,3,4] for x in load0P0.index.month] ] = None
load0P0.index = load0P0.index - pd.to_timedelta(365, unit='d') # change to 2013
# remove not in 2013 and not late months
load0P1.load0P[(load0P1.index.year != 2013) | [x in [1,2,3,4] for x in load0P1.index.month] ] = None
# append
load0P = load0P0.append(load0P1)
load0P = load0P.dropna()
# drop load0P from dataframe
df_fixed.fixed[0].drop('load0P',axis=1, inplace= True)
df_fixed.fixed[0] = pd.concat([df_fixed.fixed[0],load0P],axis=1)
# drop non 2013 from load1P
df_fixed.fixed[0].load1P[df_fixed.fixed[0].index.year != 2013] = None
# save 2015 for wind speed, convert to 2014 and recombine
wtg0WS = df_fixed.fixed[0][['wtg0WS']].copy()
wtg0WS[wtg0WS.index.year != 2012] = None
wtg0WS = wtg0WS.dropna()
wtg0WS.index = wtg0WS.index + pd.to_timedelta(365, unit='d') # change to 2013
df_fixed.fixed[0].drop('wtg0WS', axis = 1, inplace= True)
df_fixed.fixed[0] = pd.concat([df_fixed.fixed[0], wtg0WS], axis=1)
df_fixed.fixed[0].total_p.loc[df_fixed.fixed[0].index[df_fixed.fixed[0].total_p == -99999]] = None
df_fixed.fixed[0].dropna(how = 'all',inplace=True)
df_fixed.fixed[0].load1P.loc[df_fixed.fixed[0].index[df_fixed.fixed[0].load1P < 150]] = None

#df_fixed.fixed[0] = df_fixed.fixed[0].iloc[5000000:5500000]


# now fix the bad data
#df_fixed = fixBadData(df,setupDir,listOfComponents,inputDictionary['inputInterval'])

# pickle df
os.chdir(setupDir)
pickle.dump(df_fixed, open("df_fixed.p","wb"))



os.chdir(setupDir)
inFile = open("df_fixed.p","rb")
df_fixed = pickle.load(inFile)
inFile.close()
inFile = open("component.pkl","rb")
listOfComponents = pickle.load(inFile)
inFile.close()


# fix the intervals
df_fixed_interval = fixDataInterval(df_fixed,inputDictionary['outputInterval'])

# fix interval did not work great on the long time period. Manually copy and past segments to replace synthesized data
os.chdir(setupDir)
inFile = open("df_fixed_interval.p","rb")
df_fixed_interval = pickle.load(inFile)
inFile.close()
# bad interval 1 : 2013 04-26 12 am to 2013 05-01 3 am
# bad interval 2: 2013 07-26 19:00 to 07-27 6:00
plt.figure()
plt.plot(df_fixed_interval.fixed[0].load0P)
badStuff = []
badStuff = badStuff + [[pd.to_datetime('2013 04-26 00:00:00'), pd.to_datetime('2013 05-01 03:00:00')]]
badStuff = badStuff + [[pd.to_datetime('2013 07-26 19:00:00'), pd.to_datetime('2013 07-27 06:00:00')]]
badStuff = badStuff + [[pd.to_datetime('2013 01-20 18:09:33'), pd.to_datetime('2013 01-20 18:09:37')]]
badStuff = badStuff + [[pd.to_datetime('2013 03-20 23:08:49'), pd.to_datetime('2013 03-20 23:09:04')]]
badStuff = badStuff + [[pd.to_datetime('2013 03-21 00:57:30'), pd.to_datetime('2013 03-21 00:57:42')]]
#badStuff = badStuff + [[pd.to_datetime('2013 08-18 23:08:49'), pd.to_datetime('2013 08-18 23:09:04')]]
badStuff = badStuff + [[pd.to_datetime('2013 10-31 16:49:05'), pd.to_datetime('2013 10-31 16:49:15')]]
badStuff = badStuff + [[pd.to_datetime('2013 11-15 17:00:00'), pd.to_datetime('2013 11-15 20:30:00')]]
badStuff = badStuff + [[pd.to_datetime('2013 11-16 01:00:00'), pd.to_datetime('2013 11-16 09:30:00')]]
badStuff = badStuff + [[pd.to_datetime('2013 11-16 22:00:00'), pd.to_datetime('2013 11-17 09:30:00')]]

for bs in badStuff:
    plt.figure()
    plt.plot(df_fixed_interval.fixed[0].load0P.loc[
             bs[0] - pd.to_timedelta(1, unit='d'):bs[1] + pd.to_timedelta(1, unit='d')])
    df_fixed_interval.fixed[0].load0P.loc[bs[0]:bs[1]] = df_fixed_interval.fixed[0].load0P.loc[
                                                             bs[0] - pd.to_timedelta(1, unit='w'):bs[1] - pd.to_timedelta(
                                                                 1, unit='w')].values
    plt.plot(df_fixed_interval.fixed[0].load0P.loc[bs[0]:bs[1]])

# add load0 and load1 together to get combined load
dfLoad2P = pd.DataFrame({'load2P':df_fixed_interval.fixed[0].load0P + df_fixed_interval.fixed[0].load1P})
df_fixed_interval.fixed[0] = pd.concat([df_fixed_interval.fixed[0],dfLoad2P], axis=1 )

# pickle df
os.chdir(setupDir)
pickle.dump(df_fixed_interval, open("df_fixed_interval.p","wb"))

d = {}
for c in listOfComponents:
    d[c.column_name] = c.toDictionary()

# add combined load
d['load2P'] = {'scale':1, 'offset':0, 'units':'kW'}
# now convert to a netcdf

dataframe2netcdf(df_fixed_interval.fixed[0], d)
# save ncfile in folder `ModelInputData' in the path ../GBSProjects/[VillageName]/InputData/TimeSeriesData/'''
