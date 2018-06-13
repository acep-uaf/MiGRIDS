# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads dataframe of data input compares values to descriptor xmls and returns a clean dataframe from a DataClass object
# Out of bounds values for each component are replaced first, followed by datagaps and periods of inline data.
# assumes df column headings match header values in setup.xml
# assumes columns names ending in 'P' are power output components
# assumes data is ordered by time ascending and index increases with time
# a log of data that has been replaced will be generated in the TimeSeriesData folder


import xml.etree.ElementTree as ET
import os
import logging
import re
import pandas as pd
import numpy as np
from scipy import stats
from GBSInputHandler.DataClass import DataClass
from GBSInputHandler.isInline import isInline
from GBSInputHandler.badDictAdd import badDictAdd
import matplotlib.pyplot as plt


# constants
DATETIME = 'DATE'  # the name of the column containing sampling datetime as a numeric
DESCXML = 'Descriptor.xml'  # the suffix of the xml for each component that contains max/min values
TOTALP = 'total_p'  # the name of the column that contains the sum of power output for all components


# dataframe, string, list, list -> DataClass
# Dataframe is the combined dataframe consisting of all data input (multiple files may have been merged)
# SampleInterval is a list of sample intervals for each input file
# returns a DataClass object with raw and cleaned data and powercomponent information
def fixBadData(df, setupDir, ListOfComponents, sampleInterval):
   '''returns cleaned dataframe'''

   # local functions - not used outside fixBadData

   # string, dataframe, xml, dictionary -> dataframe, dictionary
   # returns a dictionary of bad values for a given variable and change out of bounds values to Nan in the dataframe
   def checkMinMaxPower(component, df, descriptorxml, baddata):
       '''change out of bounds values to be within limits'''
       # look up possible min/max
       # if it is a sink, max power is the input, else it is the output
       if getValue(descriptorxml, "type", False) == "sink":
           maxPower = getValue(descriptorxml, "PInMaxPa")
           minPower = getValue(descriptorxml, "POutMaxPa")
       else:
           maxPower = getValue(descriptorxml, "POutMaxPa")
           minPower = getValue(descriptorxml, "PInMaxPa")
       if (maxPower is not None) & (minPower is not None):
           try:
               over = df[component] > maxPower

               under = df[component] < minPower
               df[component] = data.fixed[component].mask((over | under))
               if(len(df[component][pd.isnull(df[component])].index.tolist()) > 0):
                   badDictAdd(component, baddata, '1.Exceeds Min/Max',
                           df[component][pd.isnull(df[component])].index.tolist())
           except KeyError:
               print("%s was not found in the dataframe" % component)

       return df, baddata

   # XML, String -> float
   # returns the 'value' at a specific node within an xml file.
   def getValue(xml, node, convetToFloat = True):
       '''returns the value at a specified noede within an xml file'''
       if xml.find(node) is not None:
            value = xml.find(node).attrib.get('value')
            if convetToFloat is True:
                value = float(value)
       else:
           value = 0
       return value
   
   #filename = os.path.join(setupDir + '../../TimeSeriesData', 'BadData.log')
   filename = os.path.join(setupDir, 'BadData.log')
   logging.basicConfig(filename=filename, level=logging.DEBUG, format='%(asctime)s %(message)s')
    
   # create DataClass object to store raw, fixed, and summery outputs
   # use the largest sample interval for the data class
   sampleIntervalTimeDelta = [pd.to_timedelta(s) for s in sampleInterval]
   data = DataClass(df, max(sampleIntervalTimeDelta))

   # identifies whether or not the component is a source
   # xml file -> boolean    
   def isSource(descriptorXML):
      if getValue(descriptorxml, "type") =='source' OR sinksource:
          return True
      return False
    
   # data gaps are filled with NA's to be filled later
   data.checkDataGaps()
  
  # create a list of power columns
   powerColumns = []
   eColumns = []
   loads=[]
 
   # replace out of bounds component values before we use these data to replace missing data
   for c in ListOfComponents:
##   TODO load can be identified by 'load' and component is attribute p but not load
       # seperate the component name and attribute. Eg 'wtg10WS' becomes 'wtg10' which is the component name. The use of
       # c.column_name is a bit of a misnomer in the Component class
       componentName = componentNameFromColumn(c.column_name)
       attribute = attributeFromColumn(c.column_name)
       descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([componentName, DESCXML]))
       try:
           descriptorxml = ET.parse(descriptorxmlpath)

           try:
               #if it has a p attribute it is either a powercomponent or a load and has a min/max value
               if attribute == 'P':
                   checkMinMaxPower(c, data.fixed, descriptorxml, data.baddata)
                   #if source is true in the xml the column name gets added to the powerColums list
                   if isSource(descriptorxml): ##what about batteries
                       powerColumns.append(c.column_name)
                   else:
                       loads.append(c.column_name)
                       
               elif attribute in ['WS','HS','IR']:
                   eColumns.append(c.column_name)       
           except KeyError:
               print('no column named %s' % c)
       except FileNotFoundError:
           print('Descriptor xml for %s not found' % c.column_name)
   # store the power column list in the DataClass
   data.powerComponents = powerColumns
   data.eColumns = eColumns
   data.loads = loads
   
   # recalculate total_p, data gaps will sum to 0.
   data.totalPower()
  
   # identify when the entire system was offline - not collecting any data for more than 2 time intervals.
   # grouping column is the id of groups of rows where total_p value is repeated over more that 2 timesteps
   for i,df in enumerate(data.fixed):
       #df =  df.fillna(-99999)
       df = df.replace(np.nan, -99999)
       
       df['grouping'] = 0
       df['grouping'] = isInline(df[TOTALP])
       print(df.head())
       #these are the offline groupings for e-columns 
       for e in data.ecolumns:
           df['_'.join([e,'grouping'])] = 0
           df['_'.join([e,'grouping'])] = isInline(df[e])
       
       #replace offline data for loads       
       for l in data.loads:
           df['_'.join([l,'grouping'])] = 0
           df['_'.join([l,'grouping'])] = isInline(df[l]) 
       data.fixed[i] = df
       
   #replace offline data for total power sources
   data.fixOfflineData(TOTALP)
   data.fixOfflineData(data.eColumns)
   data.fixOfflineData(data.loads)
           
   # scale data based on units and offset in the component xml file
   data.scaleData(ListOfComponents)      
 
   #reads the component descriptor files and
   #returns True if none of the components have isFrequencyReference=1 and
   #isVoltageSource = True
   def dieselNeeded(myIterator, setupDir):
       def get_next(myiter):
           try:
               return next(myiter)
           except StopIteration:
               return None

       c = get_next(myIterator)
       if c is None:
           return True

       if c.column_name in data.powerComponents:
           # TODO: see above
           descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([componentNameFromColumn(c.column_name), DESCXML]))
           try:
               descriptorxml = ET.parse(descriptorxmlpath)

               if (descriptorxml.find('isVoltageSource').attrib.get('value') == "1") & \
                         (descriptorxml.find('isFrequencyReference').attrib.get('value') == "TRUE"):
                   return False
               else:
                   return dieselNeeded(myIterator, setupDir)
           except FileNotFoundError:
               return dieselNeeded(myIterator, setupDir)
       return dieselNeeded(myIterator, setupDir)

    # fill diesel columns with a value if the system needs diesel to operate
   componentIterator = iter(ListOfComponents)
   if dieselNeeded(componentIterator,setupDir):

       data.fixGen(powerColumns)
       data.totalPower()

   data.removeAnomolies(5)
   data.totalPower()

   return data


# supporting functions for fixBadData

def attributeFromColumn(columnHeading):
    match = re.match(r"([a-z]+)([0-9]+)([A-Z]+)", columnHeading, re.I)
    if match:
        attribute = match.group(3)
        return attribute
    return

def componentNameFromColumn(columnHeading):
    match = re.match(r"([a-z]+)([0-9]+)", columnHeading, re.I)
    if match:
        name = match.group()
        return name 
    return

# list of indices, dataframe, component -> dataframe
# modifies the existing values in a dataframe using linear interpolation
def linearFix(index_list, df, component):
    for i in index_list:
        index = getIndex(df[component], i)
        x = (pd.to_timedelta(pd.Series(df.index.to_datetime()))).dt.total_seconds().astype(int)
        x.index = pd.to_datetime(df.index, unit='s')
        y = df[component]
        value = linearEstimate(x[[min(index), max(index) + 1]],
                               y[[min(index), max(index)]], x.loc[i])
        df.loc[i, component] = value
    return df


# Series, index -> list of indices
# returns the closest 2 indices of valid values to i, i can range from 0 to len(df)
def getIndex(y, i):
    base = y.index.get_loc(i)
    # check if base is an int or array, use first value if its a list
    if isinstance(base, list):
        base = base[0]
    mask = pd.Index([base]).union(pd.Index([getNext(base, y, -1)])).union(pd.Index([getNext(base, y, 1)]))
    # remove the original value from mask
    mask = mask.drop(base)
    return mask


# numeric array, numeric array, Integer -> numeric
# returns a linear estimated value for a given t value
# x is array of x values (time), y is array of y values (power), t is x value to predict for.
def linearEstimate(x, y, t):
    k = stats.linregress(x, y)
    return k.slope * t + k.intercept


# integer, Series, integer -> index
# returns the closest valid index to i
def getNext(i, l, step):
    if ((i + step) < 0) | ((i + step) >= len(l)):
        step = step * -2
        return getNext(i, l, step)
    elif not np.isnan(l[i + step]):
        return i + step
    else:
        return getNext((i + step), l, step)



