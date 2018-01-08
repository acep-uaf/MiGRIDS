# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads dataframe of data input compares values to descriptor xmls and returns a clean dataframe from a DataClass object
#assumes df column headings match header values in setup.xml
#assumes data is ordered by time ascending and index increases with time 

def fixBadData(df,setupDir,componentList,componentUnits=None,componentAttributes=None):
    import pandas as pd
    import numpy as np
    import xml.etree.ElementTree as ET
    import os
    from scipy import stats
    import logging
    import matplotlib.pyplot as plt
    
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'BadData.log')
    logging.basicConfig(filename = filename, level = logging.DEBUG, format='%(asctime)s %(message)s')
    #constants
    DATETIME = 'date' #the name of the column containing sampling datetime as a numeric
    DESCXML = 'Descriptor.xml' #the suffix of the xml for each component that contains max/min values
    COMPSUFFIX = 'p' #the suffix of that is tacked onto each component in the column name
    COMPSEPERATOR = '' #the seperator between the component and suffix for each column name
    SEARCHSTART = 1.2 * 365 * 24 * 60 * 60  #1.2 years is 3.784e+16 nanoseconds. This is how far back we want to start searching for matching data.
    MAXINLINE = 5 #up to 5 records can have the same value recorded before we call these values bad.
 
    #pandas.Series -> Dataframe
    #returns a dataframe of start and stop indices for values that are repeated (inline).
    def isInline(x):
        inline = x.reset_index(name='val').groupby(x.diff().ne(0).cumsum()).agg({'val':'first', 'index':['min','max']})
        inline.columns = inline.columns.droplevel(0)
        inline = inline.rename(columns={'first':'value','min':'start','max':'end'})
        inline['count'] = inline['end'] - inline['start']
        inline = inline[(inline['count'] > MAXINLINE) & (inline['value'] != 0)]
        return inline
    
    #String, DataFrame, Dictionary -> DataFrame, Dictionary
    #identify sequential rows with identical values for a specified component
    #inline values are replaced and index is recorded in datadictionary
    def inlineFix(component, df, baddata):  
        logging.debug("component is: %s",component)
        #identify inline values
        inline = isInline(df[component]) 
        print(inline)
        #inline values are replaced
        print('Attempting to replace %d subsets for %s.' %(len(inline), component) )
        for l in range(len(inline)):
            start_index = inline.iloc[l,]['start']
            end_index = inline.iloc[l,]['end']
            #inline values get changed to null first so they can't be used in linear interopolation
            df.loc[start_index:end_index,component] = None
            badDictAdd(component,
                     baddata,'2.Inline values',
                     df[component][pd.isnull(df[component])].index.tolist() )
        for l in range(len(inline)):
            logging.info("inline index is %d", l)
            start_index = inline.iloc[l,]['start']
            end_index = inline.iloc[l,]['end']
            #attempt to replace using direct value transfer from similar data subset or linear interpolation
            getReplacement(df,component,start_index,end_index)  
        return df, baddata
    
    #dataframe, string, integer, integer -> dataframe
    #search for a subset of data to replace block of missing values that occurrs between start and stop indices.
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
            logging.info("replaced")
            dataReplace(df, component, first_valid,start, stop)
        else:
            logging.info("interpolated")
            print ("No similar data subsets found. Using linear interpolation to replace inline values.")
            index_list = df[int(start):int(stop)].index.tolist()
            linearFix(index_list,df,component)
            
    #dataframe, string, integer, integer, integer -> dataframe
    #replaces a subset of data in a series with another subset of data of the same length from the same series
    def dataReplace(df,component, replacement_last_i, start, stop):
        df.loc[start:stop,component] = df[(replacement_last_i - (stop-start)).astype(int):(replacement_last_i + 1).astype(int)][component].values
        return df
        
    #string, dictionary, string, list of integers -> dictionary
    #adds a list of indices to a dictionary of bad values existing within a dataset.   
    def badDictAdd(component, current_dict, error_msg, index_list):
        #if the component exists add the new error message, otherwise start the compnent
        try:
            current_dict[component][error_msg]=index_list
        except KeyError:
            current_dict[component]= {error_msg:index_list}
            
    #numeric array, numeric array -> float       
    #returns the p value from the comparison of 2 distributions (x and y) using the Two-sample Kolmogorov-Smirnov Test
    def doMatch(x,y):         
        return stats.ks_2samp(x,y).pvalue
    #list of index, dataframe, component -> dataframe
    #modifies the existing values in a dataframe using linear interpolation        
    def linearFix(index_list, df,component):
         
         for i in index_list: 
             index = getIndex(df[component],i)   
             x = df[DATETIME]
             y = df[component]
             value =  linearEstimate(x[[min(index), max(index)+ 1]],
                   y[[min(index),max(index)]], x[[i]])
             df.loc[i, component]= value.tolist()[0]
             
         return df
    
    #panda.Series, integer -> list of index
    #returns the closest 2 index valid values to i, i can range from 0 to len(df)
    def getIndex(y, i):
        base = y.index.get_loc(i)
        #check if base is an int or array
        if isinstance(base,list):
            base = base[0]
        mask = pd.Index([base]).union(pd.Index([getNext(base,y,-1)])).union(pd.Index([getNext(base,y,1)]))
        #remove the original value from mask
        mask = mask.drop(base)
        return mask                    
    #numeric array, numeric array, Integer -> float  
    # X is array of x values (time), y is array of y values (power), t is x value to predict for. 
    def linearEstimate(x,y,t):    
        k = stats.linregress(x,y)
        return  k.slope *t + k.intercept  
    
    #integer, panda.Series, integer -> index 
    #returns the closest 2 index valid values to i, i can range from 0 to len(df)
    def getNext(i,l,step):
       if ((i + step) < 0 ) | ((i + step ) >= len(l)):
           step = step * -2
           return getNext(i,l,step)
       elif not np.isnan(l[i+step]):
           return i + step
       else:
           return getNext((i + step), l, step)
    
    #string, dataframe, xml, dictionary -> dataframe, dictionary
    #returns a dictionary of bad values for a given variable and change out of bounds values to Nan in the dataframe
    def checkMinMaxPower(component, df, descriptorxml,baddata):
        #look up possible min/max
        max_power = getValue(descriptorxml,"POutMaxPa")
        min_power = 0
        if (max_power == None) & (min_power == None):
            try:
                over = df[component] > max_power 
                under = df[component] < min_power
                df[component] = data.fixed[component].mask((over | under))
                badDictAdd(component,baddata,'1.Exceeds Min/Max',
                         df[component][pd.isnull(df[component])].index.tolist() )
          
            except KeyError:
                print ( "%s was not found in the dataframe" %component)
           
        return df, baddata
    
    #XML, String -> float
    #returns the 'value' at a specific node within an xml file.
    def getValue(xml, node):
        if xml.find(node) != None:
           value = float(xml.find(node).attrib.get('value'))
        else:
           value = 0
        return value 
    #string, dataframe, dictionary -> dataframe, dictionary
    #changes netagive values to 0 for the specified component. Row indexes are stored in the baddata dictionary
    def negativeToZero(component,df,baddata):
           df[df[component] < 0] = 0
           badDictAdd(component, baddata, '3.Negative value', df[df[component] < 0].index.tolist())
           return df
       
    #DataClass is object with raw_data, fixed_data,baddata dictionary, and data summaries.
    class DataClass:
       """A class with access to both raw and fixed dataframes."""
       def __init__(self, raw_df):
            self.raw = raw_df
            self.fixed = pd.DataFrame(raw_df.copy(),raw_df.index,raw_df.columns)
            self.fixed.columns = self.fixed.columns.str.lower()
            self.baddata = {}
        #summarizes raw and fixed data 
       def summarize(self):
            print('raw input summary: ')
            print(self.raw.describe())
            print('fixed output summary: ')
            print(self.fixed.describe())
            
       def visualize(self,components):
           #plot raw and fixed data
           f, axarr = plt.subplots(len(components), sharex=True)
           for i in range(len(components)):
               axarr[i].plot(self.raw[DATETIME],self.raw[components[i]])
               axarr[i].plot(self.fixed[DATETIME],self.fixed[components[i]]);
               axarr[i].set_title(component)
          
           f.subplots_adjust(hspace=0.3)
           plt.show()
  
     #dataframe, -> dataframe  
     #scales raw values to standardized units for model input
    def scaleData(df,componentUnits=None,componentAttributes=None ):
    # convert units
    # initiate lists
        units = [None] * len(componentUnits)
        scale = [None] * len(componentUnits)
        offset = [None] * len(componentUnits)
        for i in range(len(componentUnits)): # for each channel
            #TODO: finish adding code to get unit conersion file and update and convert units to default internal units and values to intergers.
            # cd to unit conventions file
            dir_path = os.path.dirname(os.path.realpath(__file__))
            unitConventionDir = dir_path +'..\\..\\GBSAnalyzer\\UnitConverters'
            # get the default unit for the data type
            units[i] = readXmlTag('internalUnitDefault.xml', ['unitDefaults',componentAttributes[i]], 'units', unitConventionDir)[0]
            # if the units don't match, convert
            if units[i].lower() != componentUnits[i].lower():
                unitConvertDir = dir_path + '..\\..\\GBSAnalyzer\\UnitConverters\\unitConverters.py'
                funcName = componentUnits[i].lower() + '2' + units[i].lower()
                # load the conversion
                spec = importlib.util.spec_from_file_location(funcName, unitConvertDir)
                uc = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(uc)
                x = getattr(uc, funcName)
                # update data
                df[useNames[i]] = x(df[useNames[i]])
            # get the scale and offset
            scale[i] = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'scale',
                               unitConventionDir)[0]
            offset[i] = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'offset',
                           unitConventionDir)[0]
            df[useNames[i]] = df[useNames[i]]*int(scale[i]) + int(offset[i])
            # get the desired data type and convert
            datatype = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'datatype',
                                unitConventionDir)
            df[useNames[i]] = df[useNames[i]].astype(datatype[0])
    
           
    #create DataClass object to store raw, fixed, and summery output
    data = DataClass(df) 
    
    #run through data checks for each component
    for component in componentList:
        descriptorxmlpath = os.path.join(setupDir,'..','Components',COMPSEPERATOR.join([component,DESCXML]))        
        try:
            descriptorxml = ET.parse(descriptorxmlpath)
            component = COMPSEPERATOR.join([component, COMPSUFFIX])
            try:
                #make negative values 0
                negativeToZero(component,data.fixed,data.baddata)
                
                #find and fix repeated values first
                inlineFix(component,data.fixed,data.baddata)
                
                #after replacing inline values replace values that are out of bounds
                #out of bounds values are set to Nan first then linear interpolation is used.
                checkMinMaxPower(component, data.fixed, descriptorxml,data.baddata)                 
                linearFix(data.fixed[data.fixed[component].isnull()].index.tolist(),
                                                 data.fixed,component) 
                scaleData(data.fixed,componentUnits, componentAttributes)
            except KeyError:
                print('no column named %s' %component)
        except FileNotFoundError:
            print ('Descriptor xml for %s not found' %component)
           
    data.summerize()
    data.visualize(componentList)
    
    return data.fixed, data.baddata


