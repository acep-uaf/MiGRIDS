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
SETUPXML = 'Setup.xml'
DESCXML = 'Descriptor.xml'
COMPSUFFIX = 'p'
SEARCHSTART = 1.2 * 365 * 24 * 60 * 60 * 1000 * 1000 * 1000 #1.2 years is 3.784e+16 nanoseconds. This is how far back we want to start searching for matching data.
MAXINLINE = 3

# reads dataframe of data input compares values to descriptor xmls and returns DataClass object
#assumes df column headings match header values in setup.xml
#assumes data is ordered by time ascending and index increases with time 

def fixBadData(df,setupDir,projectName):
     #TODO check dataframe sorting order.
    #create DataClass object to store raw, fixed, and summery output
    MyData = DataClass(df) 
    
    #run through data checks for each component
    for component in getComponents(setupDir,''.join([projectName, SETUPXML])):
        component = ''.join([component, COMPSUFFIX])
        try:
            #find repeated values first
            identifyInline(component,MyData)  
            
            dataMatchReplace(MyData.fixed, component) 
            
            #after replacing inline values replace values that are out of bounds
            checkMinMaxPower(component, MyData, setupDir) 
            
            linearFix(MyData.fixed[MyData.fixed[component].isnull()].index.tolist(),
                                             MyData.fixed,component) 
        except KeyError:
            print('no column named %s' %component)
           
    
    MyData.summerize()
    
    return MyData

def isEqual(x):
    r = x.reset_index(name='val').groupby(x.diff().ne(0).cumsum()).agg({'val':'first', 'index':['min','max']})
    r.columns = r.columns.droplevel(0)
    r = r.rename(columns={'first':'value','min':'start','max':'end'})
    r['count'] = r['end'] - r['start']
    r = r[(r['count'] > MAXINLINE) & (r['value'] != 0)]
    return r

#String, DataFrame -> DataFrame
#identify sequential rows with identical values for a specified component
def identifyInline(component, data):  
    inline = isEqual(data[component])  
    #inline values are set to NaN so they can be replaced
    for l in range(len(inline)):
        start_index = inline.iloc[l,]['start']
        end_index = inline.iloc[l,]['end']
        data.fixed.loc[start_index:end_index,component] = getReplacement(data,component,start_index,end_index)
    badDictAdd(component,
                 data.baddata,'2.Inline values',
    data.fixed[component][pd.isnull(data.fixed[component])].index.tolist() )
def getReplacement(df, component,start,stop):
        #search start is 1.2 year from missing data
        #TODO calculate startpoint in rows
        search_start = SEARCHSTART/15
        if search_start < 0:
            search_start = stop -start
        original_block =  df.loc[(start - 0.5 * (stop -start)):(stop + 0.5 * (stop -start)), component]
        #now we look for a block of time with similar distribution
        ps= df.loc[search_start: , component].rolling(stop - start).apply(lambda x: doMatch(x,original_block))
        #first_valid is the index of the last value in the subset of data that has a matching distribution to our missing data
        first_valid = (ps[ps > 0.10]).first_valid_index()
        if first_valid != None:
            dataReplace(df, component, first_valid,start, stop)
        else:
            print ("No similar data subsets found. Using linear interpolation to replace inline values.")
            index_list = df[start:stop].index.tolist()
            linearFix(index_list,df,component)
    
def badDictAdd(component, current_dict, error_msg, index_list):
    #if the component exists add the new error message, otherwise start the compnent
    try:
        current_dict[component][error_msg]=index_list
    except KeyError:
        current_dict[component]= {error_msg:index_list}
        
#DataFrame, String -> Dictionary
#returns dictionary of start and end times for blocks of null values for a component in a dataframe
#def getTimespans(df, component):
##   b = pd.DataFrame(MyData.fixed['gen1_output'].copy(),MyData.fixed['gen1_output'].index)
##
##    b[b.notnull()] = 1
#    d = df.astype(str).groupby(component).rank(ascending = True)[DATETIME] 
#    starts = df[DATETIME][d == 1 & df[component].isnull()].index.tolist()
#    d = df.astype(str).groupby(component).rank(ascending = False)[DATETIME] 
#    ends = df[DATETIME][d == 1 & df[component].isnull()].index.tolist()
#    
#    return {STARTS:starts,ENDS:ends}
#    
#Dataframe -> Dataframe
#replaces individual bad values with linear estimate from surrounding values
#def dataMatchReplace(df,component):
#    
#    #get dictionary of start and end times for blocks of missing data
#    time_dict = getTimespans(df, component)
#    
#    for block in range(0,len(time_dict[STARTS])):
#        start_index = df[df[DATETIME] == time_dict[STARTS][block]].index.tolist()[0]
#        time_span = time_dict[ENDS][block]-time_dict[STARTS][block]
#        time_span_in_rows = len(df[df[DATETIME] < time_dict[ENDS][block]]) - len(df[df[DATETIME] < time_dict[STARTS][block]])
#        #search start is 1.2 year from missing data
#        search_start = time_dict[STARTS][block] - SEARCHSTART
#        if search_start < 0:
#            search_start = time_span
#        original_block =  df[component][(df[DATETIME] > time_dict[STARTS][block] - 0.5 * time_span) & (df[DATETIME] <= time_dict['ends'][block] + 0.5 * time_span)]
#        #now we look for a block of time with similar distribution
#        ps= df[component][df[DATETIME] > search_start].rolling(time_span_in_rows).apply(lambda x: doMatch(x,original_block))
#        #first_valid is the index of the last value in the subset of data that has a matching distribution to our missing data
#        first_valid = (ps[ps > 0.10]).first_valid_index()
#        if first_valid != None:
#            dataReplace(df, component, first_valid,start_index,time_span_in_rows)
#        else:
#            print ("No similar data subsets found. Using linear interpolation to replace inline values.")
#            index_list = df[start_index:(start_index + time_span_in_rows)].index.tolist()
#            linearFix(index_list,df,component)
#    return df

#Dataframe, integer, integer, integer -> dataframe
def dataReplace(df,component, replacement_last_i, start, stop):
    df.loc[start:stop,component] = df[(replacement_last_i - (stop-start)):(replacement_last_i + 1)][component].values
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
def checkMinMaxPower(component, data, setupDir):
    #look up possible min/max
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
        self.fixed = self.fixed.sort_values([DATETIME]).reset_index(drop=True)
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
  