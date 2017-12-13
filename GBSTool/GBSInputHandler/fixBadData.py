# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import os
from scipy import stats

# reads dataframe of data input compares values to descriptor xmls and returns DataClass object
#assumes df column headings match header values in setup.xml
def fixBadData(df,setupDir,projectName):

    #create DataClass object to store raw, fixed, and summery output
    MyData = DataClass(df)
    
    #check the min and max values for variables in the component list
    for component in getComponents(setupDir,''.join([projectName, "Setup.xml"])):
        baddata = {}
        try:
           baddata['1.exceeds min/max']= checkMinMaxPower (component, df)
        except:
            print ('descriptor xml for %s not found' %component)
        MyData.baddata['_'.join([component, 'output'])] = baddata   
    #TODO add confirmation before replacing data values
    replaceBadValues(MyData)  
    summerize(MyData)
    return MyData

#DataClass -> dataframe
#returns a dataframe with mean, standard deviation, min and max for raw and fixed data
def summerize(data):
    #append raw and fixed into same dataframe
    raw = data.raw
    raw['df_type']='raw'
    fixed = data.fixed
    fixed['df_type']= 'fixed'
     
    #group by df type (raw/fixed) column
    data.summary = pd.concat([raw,fixed]).groupby('df_type').describe()
    print (data.summary)
    return data

#DataClass -> DataClass
#fills bad values in the dataframe with the mean of the surrounding 2 values, 
#if its the last value then takes mean of previous 2 values
#if its the first value takes mean of next 2 values
#how we replace values is dependent on the number of bad values

def replaceBadValues(data):
    #TODO add check for more than one sequential bad value - do something other than linear estimate
    for component in data.baddata.keys():
        component_data = data.baddata[component]
        for k in component_data.keys():
            index_list = component_data[k]
            for i in index_list:
                if i == 0:
                   data.fixed.set_value(i, component,
                                         linearEstimate(data.fixed['datetime'][i+1:i+2],
                                                  data.fixed[component][i+1:i+2],data.fixed['datetime'][i]))
                                         
                elif  i == len(data.raw) - 1:
                    data.fixed.set_value(i, component,
                                         linearEstimate(data.fixed['datetime'][i-2:i-1],
                                                 data.fixed[component][i-2:i-1],data.fixed['datetime'][i]))
                    
                else:
                    data.fixed.set_value(i, component, 
                        linearEstimate(data.fixed['datetime'][i-1:i+1],
                        data.fixed[component][i-1:i+1],data.fixed['datetime'][i]))
    print(data.fixed)  

#numeric array, numeric array, Integer -> float  
# X is array of x values (time), y is array of y values (power), t is x value to predict for. 
def linearEstimate(x,y,t):
    k = scipy.stats.linregress(x,y)
    return  k.slope *t + k.intercept  
 
#String->Dictionary
#returns a dictionary of bad values for a given variable
def checkMinMaxPower(component, df):
    bad_index = []
    #look up possible min max
    descriptorxmlpath = os.path.join(setupDir,'Components',''.join([component,"Descriptor.xml"]))
    descriptorxml = ET.parse(descriptorxmlpath)
    #TODO change hardcoding for POutMaxPa to something dynamic
    max_power = getValue(descriptorxml,"POutMaxPa")
    min_power = 0
    try:
        over = df['_'.join([component, 'output'])] > max_power
        under = df['_'.join([component, 'output'])] < min_power
        bad_data = df[over | under]['_'.join([component, 'output'])]
        bad_index = list(bad_data.to_dict().keys())
    except:
        print ('_'.join([component, 'output']) + " was not found in the dataframe")
    return bad_index

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
        self.baddata = {}
        self.summary = pd.DataFrame()
#String String-> List
#returns the list of components found in the setup xml       
def getComponents(setupDir, filename):
    #read the setup xml
   tree= ET.parse(os.path.join(setupDir,"Setup",filename))
   #read in component list
   componentList = tree.getroot().find('componentNames').find('names').attrib.get('value').split(" ")
   
   return componentList
