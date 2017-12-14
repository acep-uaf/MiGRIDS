# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import os
from scipy import stats

#constants
DATETIME = 'datetime'
SETUPXML = 'Setup.xml'
DESCXML = 'Descriptor.xml'
COMPSUFFIX = 'output'

# reads dataframe of data input compares values to descriptor xmls and returns DataClass object
#assumes df column headings match header values in setup.xml
#assumes data is ordered by time ascending and index increases with time 

def fixBadData(df,setupDir,projectName):
    #TODO check dataframe sorting order.
    #create DataClass object to store raw, fixed, and summery output
    MyData = DataClass(df)   
    #run through data checks for each component
    for component in getComponents(setupDir,''.join([projectName, SETUPXML])):
        #find repeated values first
        identifyInline(component,MyData)
        
        checkMinMaxPower(component, MyData, setupDir)       
        dataMatchReplace(MyData.fixed, component)
        
    #TODO add confirmation before replacing data values
    #replace values and summerize the differences from the original data
    
    replaceBadValues(MyData)  
    MyData.summerize()
    return MyData

#String, DataFrame -> DataFrame
#identify sequential rows with identical values for a specified component
def identifyInline(component, data):
    bad_index = []
    try: 
        data.fixed['_'.join(['diff',component])] = pd.DataFrame({
                'a':data.fixed['_'.join([component,COMPSUFFIX])].diff(1),
                'b':data.fixed['_'.join([component,COMPSUFFIX])].diff(-1)
                }).min(1)
        bad_index = data.fixed[data.fixed['_'.join(['diff',component])]==0].index.tolist()

    except KeyError:
        print('no column named %s' %'_'.join([component,COMPSUFFIX]))
    data.baddata[component]={'2.Inline values':bad_index}

#DataClass -> DataClass
#replaces individual bad values with linear estimate from surrounding values
def replaceBadValues(data):
    #TODO add check for more than one sequential bad value - do something other than linear estimate
    for component in data.baddata.keys():
        component_data = data.baddata[component]
        for k in component_data.keys():
            print ("%d records have a %s error" % (len(component_data[k]), k) )
            #TODO map data error codes
            if k == '1.exceeds min/max':
                linearFix(component_data[k],data.fixed,component)
                   
    return

def dataMatchReplace(df,component):
    #TODO write function
    #place holder replaces inline values with 300
    try:
        df.loc[df['_'.join(['diff',component])] == 0,'_'.join([component,COMPSUFFIX])]=300
    except KeyError:
        print('Column for %s does not exist' %component)
    return df
           
def linearFix(index_list, df,component):
     for i in index_list:
                
                if i == 0:
                   df.set_value(i, component,
                                         linearEstimate(df[DATETIME][i+1:i+3],
                                                  df[component][i+1:i+3],df[DATETIME][i]))
                                         
                elif  i == len(df) - 1:
                    df.set_value(i, component,
                                         linearEstimate(df[DATETIME][i-2:i],
                                                 df[component][i-2:i],df[DATETIME][i]))
                    
                else:
                    df.set_value(i, component, 
                        linearEstimate(df[DATETIME][i-1:i+1],
                        df[component][i-1:i+1],df[DATETIME][i]))
                    
#numeric array, numeric array, Integer -> float  
# X is array of x values (time), y is array of y values (power), t is x value to predict for. 
def linearEstimate(x,y,t):
    k = stats.linregress(x,y)
    return  k.slope *t + k.intercept  
    
#String, dataclass, string -> dictionary
#returns a dictionary of bad values for a given variable
def checkMinMaxPower(component, dataclass, setupDir):
    
    bad_index = []
    #look up possible min max
    descriptorxmlpath = os.path.join(setupDir,'Components',''.join([component,DESCXML]))
    try:
        descriptorxml = ET.parse(descriptorxmlpath)
            
        #TODO change hardcoding for POutMaxPa to something dynamic
        max_power = getValue(descriptorxml,"POutMaxPa")
        min_power = 0
        try:
            over = dataclass.fixed['_'.join([component, COMPSUFFIX])] > max_power 
            under = dataclass.fixed['_'.join([component, COMPSUFFIX])] < min_power
            not_in_line = dataclass.fixed['_'.join(['diff',component])] != 0
            bad_index = dataclass.fixed[(over | under) & not_in_line].index.tolist()
        except KeyError:
            print ('_'.join([component, COMPSUFFIX]) + " was not found in the dataframe")
        dataclass.baddata['_'.join([component, COMPSUFFIX])]={'1.exceeds min/max': bad_index}
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
    
#DataClass is object with raw_data, fixed_data
class DataClass:
   """A class with access to both raw and fixed dataframes."""
   def __init__(self, raw_df):
        self.raw = raw_df
        self.fixed = pd.DataFrame(raw_df.copy(),raw_df.index,raw_df.columns.str.lower())
        self.fixed['flagged'] = 0
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