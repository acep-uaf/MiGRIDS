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
import pandas as pd
import numpy as np
from scipy import stats
from DataClass import DataClass
from isInline import isInline
from badDictAdd import badDictAdd
import matplotlib.pyplot as plt


# constants
DATETIME = 'DATE'  # the name of the column containing sampling datetime as a numeric
DESCXML = 'Descriptor.xml'  # the suffix of the xml for each component that contains max/min values
TOTALP = 'total_p'  # the name of the column that contains the sum of power output for all components


# dataframe, string, list -> DataClass
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

   filename = os.path.join(setupDir + '../../TimeSeriesData', 'BadData.log')
   logging.basicConfig(filename=filename, level=logging.DEBUG, format='%(asctime)s %(message)s')

   # create DataClass object to store raw, fixed, and summery outputs
   # use the largest sample interval for the data class
   sampleIntervalTimeDelta = pd.to_timedelta(sampleInterval)
   data = DataClass(df, max(sampleIntervalTimeDelta))
   # empty list of Components to be filled
   componentList = []

   # create a list of power columns (column names ending in p)
   powerColumns = []
   for c in ListOfComponents:
       componentList.append(c.component_name)
       if c.component_name.lower()[-1:] == 'p':
           powerColumns.append(c.component_name)
   # store the power column list in the DataClass
   data.powerComponents = powerColumns
   # data gaps are filled with NA's to be filled later
   data.checkDataGaps()
   # total power is the sum of values in all the power components
   data.totalPower()

   # identify when the entire system was offline - not collecting any data for more than 2 time intervals.
   # grouping column is the id of groups of rows where total_p value is repeated over more that 2 timesteps
   data.fixed['grouping'] = 0
   data.fixed['grouping'] = isInline(data.fixed['total_p'])

   # scale data based on units and offset in the component xml file
   data.scaleData(ListOfComponents)

   # TODO: remove after testign
   plt.plot(data.fixed.total_p)
   plt.plot(data.fixed.load0P)

   '''
    # replace out of bounds component values before we use these data to replace missing data
    for c in ListOfComponents:
        if c.component_name.lower()[-1:] == 'p':
           # seperate the component name and attribute. Eg 'wtg10WS' becomes 'wtg10' which is the component name. The use of
           # c.component_name is a bit of a misnomer in the Component class
           componentName = c.component_name[0:len(c.component_name) - len(c.attribute)]
           descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([componentName, DESCXML]))
           try:
               descriptorxml = ET.parse(descriptorxmlpath)

               try:
                   checkMinMaxPower(c.component_name, data.fixed, descriptorxml, data.baddata)
               except KeyError:
                   print('no column named %s' % c.component_name)
           except FileNotFoundError:
               print('Descriptor xml for %s not found' % c.component_name)
    '''

    # TODO: remove after testign
   plt.plot(data.fixed.total_p)
   plt.plot(data.fixed.load0P)

   # recalculate total_p, data gaps will sum to 0.
   data.totalPower()

   # replace the 0's with values from elsewhere in the dataset
   # TODO: this needs to be implemnted to allow multiple data channels
   #data.fixOfflineData()

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

       if c.component_name.lower()[-1:] == 'p':
           # TODO: see above
           descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([c.component_name[0:4], DESCXML]))
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


# dataframe, dataframe, dataframe, string -> dataframe
# replaces a subset of data in a series with another subset of data of the same length from the same series
# if component is total_p then replaces all columns with replacement data
def dataReplace(df, missing, replacement, component=None):
    '''replaces the values in one dataframe with those from another'''
    if component == 'total_p':
        df.loc[min(missing.index):max(missing.index)] = replacement.values
    else:
        df.loc[min(missing.index):max(missing.index), component] = replacement[component].values
    return df

