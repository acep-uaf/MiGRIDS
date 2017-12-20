# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)


import pandas as pd
import xml.etree.ElementTree as ET
import os
from scipy import stats

#constants
DATETIME = 'datetime'
SETUPXML = 'Setup.xml'
DESCXML = 'Descriptor.xml'
COMPSUFFIX = 'output'
SEARCHSTART = 70

# reads dataframe of data input compares values to descriptor xmls and returns DataClass object
#assumes df column headings match header values in setup.xml
#assumes data is ordered by time ascending and index increases with time 

def fixBadData(df,setupDir,projectName):
    #TODO check dataframe sorting order.
    #create DataClass object to store raw, fixed, and summery output
    MyData = DataClass(df) 
    
    #run through data checks for each component
    for component in getComponents(setupDir,''.join([projectName, SETUPXML])):
        component = '_'.join([component, COMPSUFFIX])
        try:
            #find repeated values first
            identifyInline(component,MyData)           
            dataMatchReplace(MyData.fixed, component) 
            checkMinMaxPower(component, MyData, setupDir) 
            
            linearFix(MyData.fixed[MyData.fixed[component].isnull()].index.tolist(),
                                             MyData.fixed,component) 
            print(MyData.fixed)
        except KeyError:
            print('no column named %s' %component)
        #TODO add confirmation before replacing data values
       
    MyData.summerize()
    return MyData

#String, DataFrame -> DataFrame
#identify sequential rows with identical values for a specified component
def identifyInline(component, data):

    b = pd.DataFrame({
            'a':data.fixed[component].diff(1).abs(),
            'b':data.fixed[component].diff(-1).abs()
            }).min(1)==0
    
    #inline values are set to NaN so they can be replaced
    data.fixed[component] = data.fixed[component].mask(b)
    badDictAdd(component,
                 data.baddata,'2.Inline values',
    data.fixed[component][pd.isnull(data.fixed[component])].index.tolist() )
 
def badDictAdd(component, current_dict, error_msg, index_list):
    #if the component exists add the new error message, otherwise start the compnent
    try:
        current_dict[component][error_msg]=index_list
    except KeyError:
        current_dict[component]= {error_msg:index_list}
        
#DataFrame, String -> Dictionary
#returns dictionary of start and end times for blocks of null values for a component on a dataframe
def getTimespans(df, component):
    d = df.astype(str).groupby(component).rank(ascending = True)[DATETIME] 
    starts = df[DATETIME][d == 1 & df[component].isnull()].index.tolist()
    d = df.astype(str).groupby(component).rank(ascending = False)[DATETIME] 
    ends = df[DATETIME][d == 1 & df[component].isnull()].index.tolist()
    
    return {'starts':starts,'ends':ends}
    
#Dataframe -> Dataframe
#replaces individual bad values with linear estimate from surrounding values
def dataMatchReplace(df,component):
    
    #get dictionary of start and end times for blocks of missing data
    time_dict = getTimespans(df, component)
    
    for block in range(0,len(time_dict['starts'])):
        start_index = df[df[DATETIME] == time_dict['starts'][block]].index.tolist()[0]
        time_span = time_dict['ends'][block]-time_dict['starts'][block]
        time_span_in_rows = len(df[df[DATETIME] < time_dict['ends'][block]]) - len(df[df[DATETIME] < time_dict['starts'][block]])
        #search start is 1.2 year from missing data
        search_start = time_dict['starts'][block] - SEARCHSTART
        if search_start < 0:
            search_start = time_span
        original_block =  df[component][(df[DATETIME] > time_dict['starts'][block] - 0.5 * time_span) & (df[DATETIME] <= time_dict['ends'][block] + 0.5 * time_span)]
        #now we look for a block of time with similar distribution
        ps= df[component][df[DATETIME] > search_start].rolling(time_span_in_rows).apply(lambda x: doMatch(x,original_block))
        #first_valid is the index of the last value in the subset of data that has a matching distribution to our missing data
        first_valid = (ps[ps > 0.10]).first_valid_index()
        if first_valid != None:
            
            dataReplace(df, component, first_valid,start_index,time_span_in_rows)
        else:
            index_list = df[start_index:(start_index + time_span_in_rows)].index.tolist()
            linearFix(index_list,df,component)
    return df

#Dataframe, integer, integer -> dataframe
def dataReplace(df,component, replacement_last_i, start_i,replacement_length):
    df.loc[start_i:start_i + replacement_length,component] = df[(replacement_last_i - replacement_length):(replacement_last_i + 1)][component].values
    return df

def doMatch(x,y):   
    return stats.ks_2samp(x,y).pvalue
     
def linearFix(index_list, df,component):
     
     for i in index_list: 
         df.loc[i, component]= linearEstimate(df[DATETIME][getIndex(df,i,component)],df[component][getIndex(df,i,component)], df[DATETIME][i])
         
     return df
                    
#numeric array, numeric array, Integer -> float  
# X is array of x values (time), y is array of y values (power), t is x value to predict for. 
def linearEstimate(x,y,t):    
    k = stats.linregress(x,y)
    return  k.slope *t + k.intercept  

#dictionary of values that are out of bounds, dataframe, integer, component -> integer list
#returns the closest 2 index values to i, i can range from 0 to len(df)
#excludes values marked as out of range
def getIndex(df, i, component):
    component_array = df[component]
    if i == 0:
        index_array = [getNext(i,component_array), getNext(getNext(i,component_array),component_array)]
    elif i == len(df)-1:    
         index_array = [getPrevious(i,component_array), getPrevious(getPrevious(i,component_array),component_array)]
    else:
        index_array = [getPrevious(i,component_array), getNext(i,component_array)]
    return index_array
#integer, array
#returns the index of the previous valid value
def getNext(i,component):
    new_i = min(component[((component.notnull()) & (component.index > i))].index)
    return new_i

def getPrevious(i,component):
    new_i = max(component[((component.notnull()) & (component.index < i))].index)
    return new_i
#String, dataclass, string -> dictionary
#returns a dictionary of bad values for a given variable
def checkMinMaxPower(component, data, setupDir):
    #look up possible min max
    descriptorxmlpath = os.path.join(setupDir,'Components',''.join([component[0:4],DESCXML]))
    try:
        descriptorxml = ET.parse(descriptorxmlpath)
            
        #TODO change hardcoding for POutMaxPa to something dynamic
        max_power = getValue(descriptorxml,"POutMaxPa")
        min_power = 0
        try:
            over = data.fixed[component] > max_power 
            under = data.fixed[component] < min_power
            data.fixed[component] = data.fixed[component].mask((over | under))
            badDictAdd(component,data.baddata,'1.Exceeds Min/Max',
                     data.fixed[component][pd.isnull(data.fixed[component])].index.tolist() )
  
        except KeyError:
            print ( "%s was not found in the dataframe" %component)
    except FileNotFoundError:
        print ('Descriptor xml for %s not found' %component)
    return 

#XML, String -> float
#returns the value at a specific node within a parsed xml file.
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
        self.raw = raw_df
        self.fixed = pd.DataFrame(raw_df.copy(),raw_df.index,raw_df.columns.str.lower())
        self.baddata = {}
        self.raw_summary = raw_df.describe()
        self.fixed_summary = pd.DataFrame()
   
   def summerize(self):
        self.fixed_summary = self.fixed.describe()
        
#String String-> List
#returns the list of components found in the setup xml       
def getComponents(setupDir, filename):
    #read the setup xml
   tree= ET.parse(os.path.join(setupDir,"Setup",filename))
   #read in component list
   #assumes standardized xml with componentNames, names and value attribute
   componentList = tree.getroot().find('componentNames').find('names').attrib.get('value').split(" ")
   
   return componentList