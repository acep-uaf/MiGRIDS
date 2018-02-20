# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads dataframe of data input compares values to descriptor xmls and returns a clean dataframe from a DataClass object
#offline data is replaced first, followed by individual component data that is inline, and finally out of bounds values.
#assumes df column headings match header values in setup.xml
#assumes data is ordered by time ascending and index increases with time
#a log of data that has been replaced will be generated in the TimeSeriesData folder
#a pdf with graphs comparing original and fixed data will be generated in the TimeSeriesData folder


import xml.etree.ElementTree as ET
import os
import logging
import pickle
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import sqlite3 as lite

 #constants
DATETIME = 'DATE' #the name of the column containing sampling datetime as a numeric
DESCXML = 'Descriptor.xml' #the suffix of the xml for each component that contains max/min values 
TOTALP = 'total_p' #the name of the column that contains the sum of power output for all components. 
#TODO move to setup file or extract from existing info in setup file
GEN = True #does the system need diesel generators running. 

#dataframe, string, list -> DataClass
#returns a DataClass object with raw and cleaned data and powercomponent information
def fixBadData(df, setupDir, ListOfComponents, sampleInterval):
    '''returns cleaned dataframe'''  
    #local functions - not used outside fixBadData
    #string, dataframe, dictionary -> empty
    #changes netagive values to 0 for the specified component. Row indexes are stored in the baddata dictionary
#    def negativeToZero(component, df, baddata):
#        badDictAdd(component, baddata, '3.Negative value', df[df[component] < 0].index.tolist())
#        df[component][df[component] < 0] = 0
#        return df

    #String, DataFrame, Dictionary, grouped object -> DataFrame, Dictionary
    #inline values are replaced and index is recorded in datadictionary
#    def inlineFix(component, df, baddata, inline):
#        '''corrects inline data within a dataframe'''
#        logging.info("inline component is: %s", component)
#        logging.info('Attempting to replace %d subsets for %s.' %(len(inline), component))
#        
#         #here is where we actually replace values.
#        for name, group  in inline:
#            if(len(group) > 3) | (min(group[component]) != 0):
#               badDictAdd(component,
#                       baddata, '2.Inline values',
#                       group.index.tolist())
#            #attempt to replace using direct value transfer from similar data subset or linear interpolation
#               getReplacement(df, group.index, component)
#        return df, baddata

    #string, dataframe, xml, dictionary -> dataframe, dictionary
    #returns a dictionary of bad values for a given variable and change out of bounds values to Nan in the dataframe
    def checkMinMaxPower(component, df, descriptorxml, baddata):
        '''change out of bounds values to be within limits'''
        #look up possible min/max
        max_power = getValue(descriptorxml, "POutMaxPa")
        min_power = 0
        if (not max_power is None) & (not min_power is None):
            try:
                over = df[component] > max_power
                under = df[component] < min_power
                df[component] = data.fixed[component].mask((over | under))
                badDictAdd(component, baddata, '1.Exceeds Min/Max',
                           df[component][pd.isnull(df[component])].index.tolist())
            except KeyError:
                print("%s was not found in the dataframe" %component)

        return df, baddata

    #XML, String -> float
    #returns the 'value' at a specific node within an xml file.
    def getValue(xml, node):
        '''returns the value at a specified noede within an xml file'''
        if xml.find(node) != None:
            value = float(xml.find(node).attrib.get('value'))
        else:
            value = 0
        return value

    filename = os.path.join(setupDir + '../../TimeSeriesData', 'BadData.log')
    logging.basicConfig(filename=filename, level=logging.DEBUG, format='%(asctime)s %(message)s')
    #TODO remove sqlite backups
    database = 'fixedData.db'
    connection = lite.connect(database)
    
    #create DataClass object to store raw, fixed, and summery outputs
    data = DataClass(df,sampleInterval)
    #empty list of Components to be filled
    componentList = []
    #TODO is this in setup xml
    #create a list of power columns (column names ending in p)
    powerColumns = []
    for c in ListOfComponents:
        componentList.append(c.name)
        if c.name.lower()[-1:] == 'p':
            powerColumns.append(c.name)
    #store the power column list in the DataClass
    data.powerComponents = powerColumns
    
    #data gaps are filled with NA's to be filled later
    data.checkDataGaps()
    #total power is the sum of values in all the power components
    data.totalPower()
    #TODO remove sqlite backup
    data.fixed.to_sql('data_with_gaps',connection,if_exists='replace')
    connection.commit()
   
    #identify when the entire system was offline - not collecting any data for more than 2 time intervals.
    #grouping column is the id of groups of rows where total_p value is repeated over more that 2 timesteps
    data.fixed['grouping'] = 0
    data.fixed['grouping'] = isInline(data.fixed['total_p'])
    
    #TODO remove sqlite backup
    data.fixed.to_sql('data_with_grouping',connection,if_exists='replace')
    connection.commit()
  
    #scale data based on units and offset in the component xml file
    data.scaleData(ListOfComponents)
    
    #replace out of bounds component values before we use these data to replace missing data
    for c in ListOfComponents:
        if c.name.lower()[-1:] == 'p':
            descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([c.name[0:4], DESCXML]))
            try:
                descriptorxml = ET.parse(descriptorxmlpath)

                try:    
                    checkMinMaxPower(c.name, data.fixed, descriptorxml, data.baddata)
                except KeyError:
                    print('no column named %s' %c.name)
            except FileNotFoundError:
                print('Descriptor xml for %s not found' %c.name)
    #recalculate total_p, data gaps will sum to 0.
    data.totalPower()           
    #replace the 0's with values from elsewhere in the dataset
    data.fixOfflineData()
    #TODO add gen input to xml
    #if gen = true the system needs diesel generator input, if false the generator columns can all be 0
    #fill diesel columns with a value
    if GEN:
        data.fixGen(powerColumns)
        data.totalPower()
        data.removeAnomolies()
        
    data.fixed.to_sql("fixed_data", connection,if_exists='replace')       
    
    return data

#supporting functions for fixBadData
#series -> series
#returns the group id for values in the series, consecutive values will belong to the same group
def isInline(x):
    grouping = x.diff().ne(0).cumsum()

    return grouping

#string, dictionary, string, list of indices -> dictionary
#adds a list of indices to a dictionary of bad values existing within a dataset.
def badDictAdd(component, current_dict, error_msg, index_list):
    #if the component exists add the new error message to it, otherwise start a new set of component errror messages
    try:
        current_dict[component][error_msg] = index_list
    except KeyError:
        current_dict[component] = {error_msg:index_list}
    return current_dict

#list of indices, dataframe, component -> dataframe
#modifies the existing values in a dataframe using linear interpolation
def linearFix(index_list, df, component):

    for i in index_list:
        index = getIndex(df[component], i)
        x = (pd.to_timedelta(pd.Series(df.index.to_datetime()))).dt.total_seconds().astype(int)
        x.index = pd.to_datetime(df.index)
        y = df[component]
        value = linearEstimate(x[[min(index), max(index)+ 1]],
                               y[[min(index), max(index)]], x.loc[i])
        df.loc[i, component] = value
    return df

#Series, index -> list of indices
#returns the closest 2 indices of valid values to i, i can range from 0 to len(df)
def getIndex(y, i):
    base = y.index.get_loc(i)
    #check if base is an int or array, use first value if its a list
    if isinstance(base, list):
        base = base[0]
    mask = pd.Index([base]).union(pd.Index([getNext(base, y, -1)])).union(pd.Index([getNext(base, y, 1)]))
    #remove the original value from mask
    mask = mask.drop(base)
    return mask

#numeric array, numeric array, Integer -> numeric
#returns a linear estimated value for a given t value
# x is array of x values (time), y is array of y values (power), t is x value to predict for.
def linearEstimate(x, y, t):
    k = stats.linregress(x, y)
    return  k.slope *t + k.intercept

#TODO replace with pandas get_last, get_first
#integer, Series, integer -> index
#returns the closest valid index to i
def getNext(i, l, step):
    if ((i + step) < 0) | ((i + step) >= len(l)):
        step = step * -2
        return getNext(i, l, step)
    elif not np.isnan(l[i+step]):
        return i + step
    else:
        return getNext((i + step), l, step)

#dataframe, dataframe, dataframe, string -> dataframe
#replaces a subset of data in a series with another subset of data of the same length from the same series
#if component is total_p then replaces all columns with replacement data
def dataReplace(df, missing, replacement, component=None):
    '''replaces the values in one dataframe with those from another'''
    if component == 'total_p':
        df.loc[min(missing.index):max(missing.index)] = replacement.values
    else:
        df.loc[min(missing.index):max(missing.index), component] = replacement[component].values
    return df

#datetime -> boolean
#returns true if the datetime provided is a weekday
#def isWeekday(dt):
#    return bool(dt.dayofweek <= 5)

#dataframe, dataframe, dataframe,string -> dataframe
#returns scaled data to insert into missing data block
#def scaleMatch(df, missingBlock, replacement,component):
#    '''produces a model of the relationship between replacement and missing
#    data based on surrounding values and scales replacment data based on
#    the model'''
#    newreplacement = pd.DataFrame()
#    #values before and after the missing block
#    match = df.loc[:min(missingBlock.index), component][-5:]
#    new = df.loc[:min(replacement.index), component][-5:]
#    d = dict(y=np.array(match),x=np.array(new)) 
#    temporary_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in d.items() ]))
#   
#    match = df.loc[max(missingBlock.index): , component][0:5]
#    new= df.loc[max(replacement.index): , component][0:5]
#    d = dict(y=np.array(match),x=np.array(new)) 
#    temporary_df = pd.concat([temporary_df,pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in d.items() ]))])
#    temporary_df=temporary_df.dropna(0)
#    #model to rescale replacement values to values surrounding the missing block
#    try:
#        lm = stats.linregress(temporary_df['x'], temporary_df['y'])
#    except ValueError:
#        return pd.DataFrame()  
#    newreplacement = replacement[component] * lm.slope + lm.intercept
#    if component == 'total_p':        
#        #fill each component based on the proportion of the total it is in the replacement block
#        adjuster = np.mean(replacement)/np.mean(replacement[component]) 
#        
#    elif component == 'gentotal':
#        #TODO remove hardwire for generator columns 
#        genColumns = ['gen1P','gen2P','gen3P']
#        adjuster = np.mean(replacement[genColumns])/np.mean(replacement[component]) 
#    n = newreplacement.apply(lambda x : x * adjuster)
# 
#
#    #newreplacement = n.transpose() 
#    #reorder t he columns to match the missing block
#    #newreplacement = newreplacement[replacement.columns]
#    return n

#dataframe, list of indices, string -> Boolean
#returns true if a replacement was made, false if it was not
def getReplacement(df, indices, component = None):
     #index,range in same units as index, dataframe, dataframe, index
    def getReplacementStart(searchStart, searchRange, df, missingBlock, directMatch = None):
         #if there is a match then we can stop looking,
         #otherwise we increment our search window by a year and look again
         #start is the index of our first missing record
         start = min(missingBlock.index)
         #searchBlock is the portion of the dataframe that we will search for a match in
         searchBlock = df[searchStart: searchStart + searchRange]
         #restrict the search to only matching days of the week and time of day
         searchBlock = searchBlock[(searchBlock.index.to_datetime().dayofweek == start.dayofweek)]
         searchBlock = searchBlock.between_time((start + pd.Timedelta(hours = 3)).time(),
                             (start - pd.Timedelta(hours = 3)).time())
       
         #find the match in the searchBlock as long as it isn't empty
         if not searchBlock.empty:
          #order by proximity
             doy = start.dayofyear
             searchBlock['doydiff'] = abs(searchBlock.index.to_datetime().dayofyear - doy)
             searchBlock['hourdiff'] = abs(searchBlock.index.to_datetime().hour - start.hour)
             searchBlock['mindiff'] = abs(searchBlock.index.to_datetime().minute - start.minute)

             sortedSearchBlock = searchBlock.sort_values(['doydiff','hourdiff','mindiff'])
             #if replacment is long enough return indices, otherwise move on
             blockLength = df[min(sortedSearchBlock.index):max(sortedSearchBlock.index)][::-1].rolling(len(missingBlock)).apply(lambda x: len(x))[::-1]
             #a matching record is one that is the same day of the week, similar time of day and has enough valid records following it to fill the empty block
             directMatch = blockLength[blockLength == len(missingBlock)].first_valid_index()
         #move the search window to the following year   
         searchStart = searchStart+ pd.DateOffset(years=1)
         searchBlock = df[searchStart: searchStart + searchRange]
         #if we found a match return its index otherwise look again
         if directMatch is not None:
             return directMatch
         elif searchBlock.empty :
             #if theere is no where left to search return false
             return False
         else:
             #keep looking on the remainder of the list
             return getReplacementStart(searchStart,searchRange, df,missingBlock, directMatch)
     
     #dataframe, index, dataframe, string -> null
     #replaces a block of data and logs the indeces as bad records
    def replaceRecords(df,replacementStart, missingBlock,component):
         window = len(missingBlock)
         #TODO what is the shape of replacement if component is a list?
         replacement = df[replacementStart:][0:window]
         addin = " scaled values from "
         dataReplace(df, missingBlock, replacement,component)
         
         logging.info("replaced inline values %s through %s with %s %s through %s."
                     %(str(min(missingBlock.index)), str(max(missingBlock.index)), addin, str(min(replacement.index)), str(max(replacement.index))))
         return
    #dataframe -> index, timedelta
    #returns the a window of time that should be searched for replacement values depending on the amount of time covered in the missing block
    def getMoveAndSearch(missingBlock):
        
        #for large missing blocks of data we use a larger possible search range
        if (missingBlock.index.max(0) - missingBlock.index.min(0)) >= pd.Timedelta('1 days'):
            initialMonths = 2
            searchRange = pd.DateOffset(months=4)
        elif (missingBlock.index.max(0) - missingBlock.index.min(0)) <= pd.Timedelta('1 days'):
            initialMonths = 1
            searchRange = pd.DateOffset(weeks=8)
        #start is the missingblock minus a year and the searchrange
        searchStart= missingBlock.index[0] - pd.DateOffset(years=1, months=initialMonths, days=14)
        return searchStart, searchRange


    #get the block of missing data
    missingBlock = df.loc[indices]
    #search start is datetime indicating the start of the block of data to be searched
    #searchRange indicates how big of a block of time to search
    searchStart, searchRange = getMoveAndSearch(missingBlock)
    #replacementStart is a datetime indicating the first record in the block of replacementvalues
    replacementStart = getReplacementStart(searchStart,searchRange,df,missingBlock)
    if replacementStart:
         #replace the bad records
         replaceRecords(df,replacementStart,missingBlock,component)
         return True
    elif len(missingBlock) <= 15:
         #if we didn't find a replacement and its only a few missing records us linear estimation
         index_list = missingBlock.index.tolist()
         linearFix(index_list, df, component) 
         logging.info("No similar data subsets found. Using linear interpolation to replace inline values %s through %s."
                     %(str(min(missingBlock.index)), str(max(missingBlock.index))))
         return True
    else:
         logging.info("could not replace values %s through %s." %(str(min(missingBlock.index)), str(max(missingBlock.index))))
         return False
    
#listOfComponents -> listOfComponents
#returns a list of components that are diesel generators (start with 'gen')
def identifyGenColumns(componentList):
    genColumns = []
    for c in componentList:
        if (c[:3].lower() == 'gen') & (c[-1].lower() == 'p'):
            genColumns.append(c)
    return genColumns

#DataClass is object with raw_data, fixed_data,baddata dictionary, and system characteristics.
class DataClass:
    """A class with access to both raw and fixed dataframes."""
    def __init__(self, raw_df, sampleInterval):
        if len(raw_df) > 0:
            self.raw = raw_df.copy()
            self.fixed = pd.DataFrame(raw_df.copy(), raw_df.index, raw_df.columns)
            #give the fixed data a time index to work with - assumes this is in the first column
            time_index = pd.to_datetime(self.fixed.iloc[:, 0], unit='s')
            self.fixed.index = time_index            
            self.fixed = self.fixed.drop(self.fixed.iloc[:, 0], axis=1)
        else:
            self.raw = pd.DataFrame()
            self.fixed = pd.DataFrame()
        self.timeInterval = sampleInterval
        self.powerComponents = []
        self.baddata = {}
    #summarizes raw and fixed data and print resulting dataframe descriptions
    def summarize(self):
        '''prints basic statistics describing raw and fixed data'''
        print('raw input summary: ')
        print(self.raw.describe())
        print('fixed output summary: ')
        print(self.fixed.describe())
        
    #identifies when there are no generator values
    #if the system can't operate withouth the generators (GEN = True) then values are filled 
    #with data from a matching time of day (same as offline values)
    #list -> null
    def fixGen(self,componentList):
        gencolumns = identifyGenColumns(componentList)
        self.fixed['gentotal'] = self.fixed[gencolumns].sum(1)
        self.fixed['grouping'] =  isInline(self.fixed['gentotal'])
        groups= self.fixed.groupby(self.fixed['grouping'], as_index = True)

        logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced'  %(len(groups), len(self.fixed[pd.isnull(self.fixed.total_p)])))
        #record the offline records in our baddata dictionary
        badDictAdd('gen',
                   self.baddata, '4.Generator offline',
                   self.fixed[pd.isnull(self.fixed.gentotal)].index.tolist())
        #self.fixed.gentotal[self.fixed.gentotal == 0] = None
        self.fixed.gentotal.replace(0,np.nan)
        for name, group in groups:
            if min(group.gentotal) == 0:
                
                getReplacement(self.fixed, group.index,gencolumns)
        
        self.fixed = self.fixed.drop('gentotal',1)
        return
    
    #list, string -> pdf
    def visualize(self, components, setupDir):
        '''produces a pdf comparing raw and fixed data'''
        filename = os.path.join(setupDir + '../../TimeSeriesData', 'fixed_data_compare.pdf')

        #plot raw and fixed data
        with PdfPages(filename) as pdf:
            #plot the raw data
            plt.figure(figsize=(8 ,6))
            plt.plot(pd.to_datetime(self.raw.DATE, unit = 's'), self.raw.total_p)
            plt.title('Raw data total power')
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()
            #plot the fixed data
            plt.figure(figsize=(8, 6))
            plt.plot(self.fixed.index, self.fixed.total_p, 'b-')
            plt.title('Fixed data total power')
            pdf.savefig()
            plt.close()
            #individual component plots
            f, axarr = plt.subplots(len(components), sharex=True)
            for i in range(len(components)):
                if len(self.fixed) == len(self.raw):
                    axarr[i].plot(self.fixed.index, self.raw[components[i]])
                axarr[i].plot(self.fixed.index, self.fixed[components[i].lower()])
                axarr[i].set_title(components[i])
            f.subplots_adjust(hspace=0.3)
            pdf.savefig()
            
#    #string -> pickle
    def preserve(self,setupDir):
        '''pickles the dataframe so it can be restored later'''
        filename = os.path.join(setupDir + '../../TimeSeriesData', 'fixed_data.pickle')
        pickle_out = open(filename, 'wb')
        pickle.dump(self.fixed, pickle_out)
        pickle_out.close
        return

    #fills in records at specified time interval where no data exists. 
    #new records will have NA for values
    def checkDataGaps(self):   
        timeDiff =  pd.Series(self.fixed.index.to_datetime(), self.fixed.index).diff()
        timeDiff = timeDiff.sort_index(0,ascending=True)
        timeDiff = timeDiff[timeDiff > 2 * pd.to_timedelta(self.timeInterval)]
        #fill the gaps with NA
        for i in timeDiff.index:
           resample_df = self.fixed.loc[:i][-2:]
           resample_df = resample_df.resample(self.timeInterval).mean()
           self.fixed = self.fixed.append(resample_df[:-1])
           self.fixed = self.fixed.sort_index(0, ascending = True)
        return
    
    #sums the power columns into a single column
    def totalPower(self):
        self.fixed[TOTALP] = self.fixed[self.powerComponents].sum(1)
        self.raw[TOTALP] = self.raw[self.powerComponents].sum(1)
        return
    #List of Components -> null
    #scales raw values to standardized units for model input
    def scaleData(self, ListOfComponents):
        for c in ListOfComponents:
            c.setDatatype(self.fixed)
        return
    
    #replaces time interval data where the power output drops significanly with similar profiled data
    def removeAnomolies(self):  
        mean = np.mean(self.fixed.total_p)
        std = np.std(self.fixed.total_p)
        self.fixed[self.fixed.total_p < mean - 3 * std] = None
        #this may leave the value too high
        self.fixed = self.fixed.interpolate()
        self.totalPower()     
        return 
    

    #fills values for all components for time blocks when data collection was offline
    def fixOfflineData(self):
        #find offline time blocks
        groups= self.fixed.groupby(self.fixed['grouping'], as_index = True)

        logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced'  %(len(groups), len(self.fixed[pd.isnull(self.fixed.total_p)])))
        #record the offline records in our baddata dictionary
        badDictAdd(TOTALP,
                   self.baddata, '4.Offline',
                   self.fixed[pd.isnull(self.fixed.total_p)].index.tolist())
       
        self.fixed.total_p.replace(0,None)
        #based on our list of bad groups of data, replace the values
        for name, group in groups:
            if(len(group) > 3) | (min(group.total_p) == 0):               
                getReplacement(self.fixed, group.index,'total_p')
        return
    
