# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)


import pandas as pd
import xml.etree.ElementTree as ET
import os
from scipy import stats

#constants
DATETIME = 'date'

DESCXML = 'Descriptor.xml'
COMPSUFFIX = 'p'
COMPSEPERATOR = ''
SEARCHSTART = 1.2 * 365 * 24 * 60 * 60 * 1000 * 1000 * 1000 #1.2 years is 3.784e+16 nanoseconds. This is how far back we want to start searching for matching data.
MAXINLINE = 5
SAMPLE_INTERVAL = 15 * 1000 * 1000 * 1000 #sample interval is 15 seconds

# reads dataframe of data input compares values to descriptor xmls and returns DataClass object
#assumes df column headings match header values in setup.xml
#assumes data is ordered by time ascending and index increases with time 

def fixBadData(df,setupDir,componentList):
     #TODO check dataframe sorting order.
    #create DataClass object to store raw, fixed, and summery output
    data = DataClass(df) 
    
    #run through data checks for each component
    for component in componentList:
        descriptorxmlpath = os.path.join(setupDir,'..','Components',COMPSEPERATOR.join([component,DESCXML]))
        print(descriptorxmlpath)
        try:
            descriptorxml = ET.parse(descriptorxmlpath)
            
            component = COMPSEPERATOR.join([component, COMPSUFFIX])
            try:
                #find and fix repeated values first
                inlineFix(component,data)
                
                #after replacing inline values replace values that are out of bounds
                checkMinMaxPower(component, data, descriptorxml) 
                
                linearFix(data.fixed[data.fixed[component].isnull()].index.tolist(),
                                                 data.fixed,component) 
            except KeyError:
                print('no column named %s' %component)
        except FileNotFoundError:
            print ('Descriptor xml for %s not found' %component)
           
    
    data.summerize()
    
    return data

def isInline(x):
    inline = x.reset_index(name='val').groupby(x.diff().ne(0).cumsum()).agg({'val':'first', 'index':['min','max']})
    inline.columns = inline.columns.droplevel(0)
    inline = inline.rename(columns={'first':'value','min':'start','max':'end'})
    inline['count'] = inline['end'] - inline['start']
    inline = inline[(inline['count'] > MAXINLINE) & (inline['value'] != 0)]
    return inline

#String, DataFrame -> DataFrame
#identify sequential rows with identical values for a specified component
def inlineFix(component, data):  
    #identify inline values
    inline = isInline(data.fixed[component])  
    #inline values are replaced
    print('Attempting to replace %d subsets for %s.' %(len(inline), component) )
    for l in range(len(inline)):
        start_index = inline.iloc[l,]['start']
        end_index = inline.iloc[l,]['end']
        #inline values get changed to null first so they can't be used in linear interopolation
        data.fixed.loc[start_index:end_index,component] = None
        badDictAdd(component,
                 data.baddata,'2.Inline values',
                 data.fixed[component][pd.isnull(data.fixed[component])].index.tolist() )
    for l in range(len(inline)):
        start_index = inline.iloc[l,]['start']
        end_index = inline.iloc[l,]['end']
        #attempt to replace using direct value transfer from similar data subset or linear interpolation
        getReplacement(data.fixed,component,start_index,end_index)  
    return data
#search for a subset of data to replace block of missing values.
#if a suitable block of values is not identified linear interpolation is used.
def getReplacement(df, component,start,stop):
        #search start is 1.2 year from start of missing data block.
        search_start = df.loc[start,DATETIME] - SEARCHSTART
        window = int(stop-start)
        if (search_start < 0) | (len(df[df[DATETIME] > search_start]) < stop-start):
           start_search_here = window
        else:
            start_search_here = df[df[DATETIME] > search_start].index.tolist()[0]
        original_block =  df.loc[(start - 0.5 * window):(stop + 0.5 * window), component]
        #now we look for a block of time with similar distribution
        ps= df.loc[start_search_here: , component].rolling(window).apply(lambda x: doMatch(x,original_block))
        #first_valid is the index of the last value in the subset of data that has a matching distribution to our missing data
        first_valid = (ps[ps > 0.05]).first_valid_index()
        #if we found a suitable block of values we insert them into the missing values otherwise we interpolate the missing values
        if first_valid != None:
            dataReplace(df, component, first_valid,start, stop)
        else:
            print ("No similar data subsets found. Using linear interpolation to replace inline values.")
            index_list = df[int(start):int(stop)].index.tolist()
            linearFix(index_list,df,component)
            
#replaces a subset of data in a series with another subset of data of the same length from the same series
def dataReplace(df,component, replacement_last_i, start, stop):
    df.loc[start:stop,component] = df[(replacement_last_i - (stop-start)):(replacement_last_i + 1)][component].values
    return df

#adds a list of indices to a dictionary of bad values existing within a dataset.   
def badDictAdd(component, current_dict, error_msg, index_list):
    #if the component exists add the new error message, otherwise start the compnent
    try:
        current_dict[component][error_msg]=index_list
    except KeyError:
        current_dict[component]= {error_msg:index_list}
        
def doMatch(x,y): 
    
    return stats.ks_2samp(x,y).pvalue
     
def linearFix(index_list, df,component):
     
     for i in index_list: 
         df.loc[i, component]= linearEstimate(df[DATETIME][getIndex(df,i,component)],
               df[component][getIndex(df,i,component)], df[DATETIME][i])
         
     return df
                    
#numeric array, numeric array, Integer -> float  
# X is array of x values (time), y is array of y values (power), t is x value to predict for. 
def linearEstimate(x,y,t):    
    k = stats.linregress(x,y)
    return  k.slope *t + k.intercept  

# dataframe, integer, component -> integer list
#returns the closest 2 index valid values to i, i can range from 0 to len(df)
def getIndex(df, i, component):
    
    #integer, array
    #returns the index of the previous valid value
    def getNext(i,component):
        new_i = min(component[((component.notnull()) & (component.index > i))].index)
        return new_i
    
    def getPrevious(i,component):
        new_i = max(component[((component.notnull()) & (component.index < i))].index)
        return new_i
    
    component_array = df[component]
    if i == 0:
        index_array = [getNext(i,component_array), getNext(getNext(i,component_array),component_array)]
    elif i == len(df)-1:    
         index_array = [getPrevious(i,component_array), getPrevious(getPrevious(i,component_array),component_array)]
    else:
        index_array = [getPrevious(i,component_array), getNext(i,component_array)]
    return index_array

#String, dataclass, string -> dictionary
#returns a dictionary of bad values for a given variable
def checkMinMaxPower(component, data, descriptorxml):
    #look up possible min/max
    max_power = getValue(descriptorxml,"POutMaxPa")
    min_power = 0
    if (max_power == None) & (min_power == None):
        try:
            over = data.fixed[component] > max_power 
            under = data.fixed[component] < min_power
            data.fixed[component] = data.fixed[component].mask((over | under))
            badDictAdd(component,data.baddata,'1.Exceeds Min/Max',
                     data.fixed[component][pd.isnull(data.fixed[component])].index.tolist() )
      
        except KeyError:
            print ( "%s was not found in the dataframe" %component)
       
    return 

#XML, String -> float
#returns the 'value' at a specific node within an xml file.
def getValue(xml, node):
    if xml.find(node) != None:
       value = float(xml.find(node).attrib.get('value'))
    else:
       value = 0
    return value    
    
#DataClass is object with raw_data, fixed_data,baddata dictionary, and raw data summary.
class DataClass:
   """A class with access to both raw and fixed dataframes."""
   #TODO drop raw data
   def __init__(self, raw_df):
        #self.raw = raw_df
        self.fixed = pd.DataFrame(raw_df.copy(),raw_df.index,raw_df.columns)
        self.fixed.columns = self.fixed.columns.str.lower()
        
        self.baddata = {}
        self.raw_summary = raw_df.describe()
        self.fixed_summary = pd.DataFrame()
   
   def summerize(self):
        self.fixed_summary = self.fixed.describe()
        
