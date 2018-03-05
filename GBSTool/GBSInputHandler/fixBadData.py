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
import pickle
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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
       maxPower = getValue(descriptorxml, "POutMaxPa")
       minPower = 0
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
   def getValue(xml, node):
       '''returns the value at a specified noede within an xml file'''
       if xml.find(node) is not None:
           value = float(xml.find(node).attrib.get('value'))
       else:
           value = 0
       return value

   filename = os.path.join(setupDir + '../../TimeSeriesData', 'BadData.log')
   logging.basicConfig(filename=filename, level=logging.DEBUG, format='%(asctime)s %(message)s')

   # create DataClass object to store raw, fixed, and summery outputs
   data = DataClass(df, sampleInterval)
   # empty list of Components to be filled
   componentList = []

   # create a list of power columns (column names ending in p)
   powerColumns = []
   for c in ListOfComponents:
       componentList.append(c.name)
       if c.name.lower()[-1:] == 'p':
           powerColumns.append(c.name)
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

   # replace out of bounds component values before we use these data to replace missing data
   for c in ListOfComponents:
       if c.name.lower()[-1:] == 'p':
           descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([c.name[0:4], DESCXML]))
           try:
               descriptorxml = ET.parse(descriptorxmlpath)

               try:
                   checkMinMaxPower(c.name, data.fixed, descriptorxml, data.baddata)
               except KeyError:
                   print('no column named %s' % c.name)
           except FileNotFoundError:
               print('Descriptor xml for %s not found' % c.name)
   # recalculate total_p, data gaps will sum to 0.
   data.totalPower()

   # replace the 0's with values from elsewhere in the dataset
   data.fixOfflineData()

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

       if c.name.lower()[-1:] == 'p':
           descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([c.name[0:4], DESCXML]))
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

   data.removeAnomolies()
   data.totalPower()

   return data


# supporting functions for fixBadData
# series -> series
# returns the group id for values in the series, consecutive values will belong to the same group
def isInline(x):
    grouping = x.diff().ne(0).cumsum()
    return grouping


# string, dictionary, string, list of indices -> dictionary
# adds a list of indices to a dictionary of bad values existing within a dataset.
def badDictAdd(component, current_dict, error_msg, index_list):
    # if the component exists add the new error message to it, otherwise start a new set of component errror messages
    try:
        current_dict[component][error_msg] = index_list
    except KeyError:
        current_dict[component] = {error_msg: index_list}
    return current_dict


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

# TODO PERFORMANCE  slowest part of module because iterates through every missing interval
# dataframe, list of indices, string -> Boolean
# returns true if a replacement was made, false if it was not
def getReplacement(df, indices, component=None):
    # index,range in same units as index, dataframe, dataframe, index
    def getReplacementStart(dtStart, timeRange, entiredf, missingdf, directMatch=None):
        # if there is a match then stop looking,
        # otherwise increment the search window by a year and look again
        # start is the index of our first missing record
        start = min(missingdf.index)
        # searchBlock is the portion of the dataframe that we will search for a match in
        searchBlock = entiredf.loc[dtStart: dtStart + timeRange]
        # restrict the search to only matching days of the week and time of day
        searchBlock = searchBlock[(searchBlock.index.to_datetime().dayofweek == start.dayofweek)]
        searchBlock = searchBlock.between_time((start + pd.Timedelta(hours=3)).time(),
                                               (start - pd.Timedelta(hours=3)).time())

        # find the match in the searchBlock as long as it isn't empty
        if not searchBlock.empty:
            # order by proximity

            searchBlock['newtime'] = pd.Series(searchBlock.index.to_datetime(), searchBlock.index).apply(
                lambda dt: dt.replace(year=start.year))

            searchBlock['timeapart'] = searchBlock['newtime'] - start
            sortedSearchBlock = searchBlock.sort_values('timeapart')
            # if replacment is long enough return indices, otherwise move on
            blockLength = entiredf[min(sortedSearchBlock.index):max(sortedSearchBlock.index)][::-1].rolling(
                len(missingdf)).count()[::-1]

            # a matching record is one that is the same day of the week, similar time of day and has enough
            # valid records following it to fill the empty block
            directMatch = blockLength[blockLength == len(missingdf)].first_valid_index()
        # move the search window to the following year
        dtStart = dtStart + pd.DateOffset(years=1)
        searchBlock = entiredf[dtStart: dtStart + timeRange]
        # if we found a match return its index otherwise look again
        if directMatch is not None:
            return directMatch
        elif searchBlock.empty:
            # if theere is no where left to search return false
            return False
        else:
            # keep looking on the remainder of the list
            return getReplacementStart(dtStart, timeRange, entiredf, missingdf, directMatch)

    # dataframe, index, dataframe, string -> null
    # replaces a block of data and logs the indeces as bad records
    def replaceRecords(entiredf, dtStart, missingdf, strcomponent):
        window = len(missingdf)
        # TODO what is the shape of replacement if component is a list?
        replacement = entiredf[dtStart:][0:window]
        addin = " scaled values from "
        dataReplace(entiredf, missingdf, replacement, strcomponent)

        logging.info("replaced inline values %s through %s with %s %s through %s."
                     % (str(min(missingdf.index)), str(max(missingdf.index)), addin, str(min(replacement.index)),
                        str(max(replacement.index))))
        return

    # dataframe -> index, timedelta
    # returns the a window of time that should be searched for replacement values depending on the
    # amount of time covered in the missing block
    def getMoveAndSearch(missingdf):

        # for large missing blocks of data we use a larger possible search range
        if (missingdf.index.max(0) - missingdf.index.min(0)) >= pd.Timedelta('1 days'):
            initialMonths = 2
            timeRange = pd.DateOffset(months=4)
        else:
            initialMonths = 1
            timeRange = pd.DateOffset(weeks=8)
        # start is the missingblock minus a year and the searchrange
        dtStart = missingdf.index[0] - pd.DateOffset(years=1, months=initialMonths, days=14)
        return dtStart, timeRange

    # get the block of missing data
    missingBlock = df.loc[indices]
    # search start is datetime indicating the start of the block of data to be searched
    # searchRange indicates how big of a block of time to search
    searchStart, searchRange = getMoveAndSearch(missingBlock)

    # replacementStart is a datetime indicating the first record in the block of replacementvalues
    replacementStart = getReplacementStart(searchStart, searchRange, df, missingBlock)
    if replacementStart:
        # replace the bad records
        replaceRecords(df, replacementStart, missingBlock, component)
        return True
    elif len(missingBlock) <= 15:
        # if we didn't find a replacement and its only a few missing records us linear estimation
        index_list = missingBlock.index.tolist()
        linearFix(index_list, df, component)
        logging.info("No similar data subsets found. Using linear interpolation to replace inline values %s through %s."
                     % (str(min(missingBlock.index)), str(max(missingBlock.index))))
        return True
    else:
        logging.info(
            "could not replace values %s through %s." % (str(min(missingBlock.index)), str(max(missingBlock.index))))
        return False


# listOfComponents -> listOfComponents
# returns a list of components that are diesel generators (start with 'gen')
def identifyGenColumns(componentList):
    genColumns = []
    for c in componentList:
        if (c[:3].lower() == 'gen') & (c[-1].lower() == 'p'):
            genColumns.append(c)
    return genColumns


# DataClass is object with raw_data, fixed_data,baddata dictionary, and system characteristics.
class DataClass:
    """A class with access to both raw and fixed dataframes."""

    def __init__(self, raw_df, sampleInterval):
        if len(raw_df) > 0:
            self.raw = raw_df.copy()
            self.fixed = pd.DataFrame(raw_df.copy(), raw_df.index, raw_df.columns)
            # give the fixed data a time index to work with - assumes this is in the first column
            time_index = pd.to_datetime(self.fixed.iloc[:, 0], unit='s')

            self.fixed = self.fixed.drop(self.fixed.columns[0], axis=1)
            self.fixed.index = time_index
        else:
            self.raw = pd.DataFrame()
            self.fixed = pd.DataFrame()
        self.timeInterval = sampleInterval
        self.powerComponents = []
        self.baddata = {}
        return

    # DataClass -> null
    # summarizes raw and fixed data and print resulting dataframe descriptions
    def summarize(self):
        '''prints basic statistics describing raw and fixed data'''
        print('raw input summary: ')
        print(self.raw.describe())
        print('fixed output summary: ')
        print(self.fixed.describe())
        return

    # list -> null
    # identifies when there are no generator values
    # if the system can't operate withouth the generators (GEN = True) then values are filled
    # with data from a matching time of day (same as offline values)
    def fixGen(self, componentList):
        gencolumns = identifyGenColumns(componentList)
        self.fixed['gentotal'] = self.fixed[gencolumns].sum(1)
        self.fixed['grouping'] = isInline(self.fixed['gentotal'])
        groups = self.fixed.groupby(self.fixed['grouping'], as_index=True)

        logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (
            len(groups), len(self.fixed[pd.isnull(self.fixed.total_p)])))
        # record the offline records in our baddata dictionary
        badDictAdd('gen',
                   self.baddata, '2.Generator offline',
                   self.fixed[self.fixed.gentotal==0].index.tolist())

        self.fixed.gentotal.replace(0, np.nan)
        for name, group in groups:
            if min(group.gentotal) == 0:
                getReplacement(self.fixed, group.index, gencolumns)

        self.fixed = self.fixed.drop('gentotal', 1)
        return

    # list, string -> pdf
    # creates a pdf comparing raw and fixed data values
    def visualize(self, components, setupDir):
        filename = os.path.join(setupDir, '../TimeSeriesData', 'fixed_data_compare.pdf')

        # plot raw and fixed data
        with PdfPages(filename) as pdf:
            # plot the raw data
            plt.figure(figsize=(8, 6))
            plt.plot(pd.to_datetime(self.raw.DATE, unit='s'), self.raw[TOTALP])
            plt.title('Raw data total power')
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()
            # plot the fixed data
            plt.figure(figsize=(8, 6))
            plt.plot(self.fixed.index, self.fixed[TOTALP], 'b-')
            plt.title('Fixed data total power')
            pdf.savefig()
            plt.close()

    # DataClass string -> pickle
    # pickles the dataframe so it can be restored later
    def preserve(self, setupDir):
        filename = os.path.join(setupDir + '../TimeSeriesData', 'fixed_data.pickle')
        pickle_out = open(filename, 'wb')
        pickle.dump(self.fixed, pickle_out)
        pickle_out.close
        return

    # DataClass->null
    # fills in records at specified time interval where no data exists.
    # new records will have NA for values
    def checkDataGaps(self):
        timeDiff = pd.Series(pd.to_datetime(self.fixed.index, unit='s'), self.fixed.index).diff()
        timeDiff = timeDiff.sort_index(0, ascending=True)
        timeDiff = timeDiff[timeDiff > 2 * pd.to_timedelta(self.timeInterval)]
        # fill the gaps with NA
        for i in timeDiff.index:
            resample_df = self.fixed.loc[:i][-2:]
            resample_df = resample_df.resample(self.timeInterval).mean()
            self.fixed = self.fixed.append(resample_df[:-1])
            self.fixed = self.fixed.sort_index(0, ascending=True)
        return

    # Dataclass -> null
    # sums the power columns into a single column
    def totalPower(self):
        self.fixed[TOTALP] = self.fixed[self.powerComponents].sum(1)
        self.raw[TOTALP] = self.raw[self.powerComponents].sum(1)
        return

    # List of Components -> null
    # scales raw values to standardized units for model input
    def scaleData(self, ListOfComponents):
        for c in ListOfComponents:
            c.setDatatype(self.fixed)
        return

    # DataClass -> null
    # replaces time interval data where the power output drops or increases significantly
    # compared to overall data characteristics
    def removeAnomolies(self):
        mean = np.mean(self.fixed[TOTALP])
        std = np.std(self.fixed[TOTALP])
        #self.fixed[(self.fixed[TOTALP] < mean - 3 * std)] = None
        self.fixed[(self.fixed[TOTALP] < mean - 3 * std) | (self.fixed[TOTALP] > mean + 3 * std)] = None
        # replace values with linear interpolation from surrounding values
        self.fixed = self.fixed.interpolate()
        self.totalPower()
        return

    # DataClass -> null
    # fills values for all components for time blocks when data collection was offline
    def fixOfflineData(self):
        # find offline time blocks
        groups = self.fixed.groupby(self.fixed['grouping'], as_index=True)

        logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (
            len(groups), len(self.fixed[pd.isnull(self.fixed.total_p)])))
        # record the offline records in our baddata dictionary
        badDictAdd(TOTALP,
                   self.baddata, '2.Offline',
                   self.fixed[pd.isnull(self.fixed[TOTALP])].index.tolist())

        self.fixed[TOTALP].replace(0, None)
        # based on our list of bad groups of data, replace the values
        for name, group in groups:
            if (len(group) > 3) | (min(group[TOTALP]) == 0):
                getReplacement(self.fixed, group.index, 'total_p')
        return
