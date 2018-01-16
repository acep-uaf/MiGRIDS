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
    from readXmlTag import readXmlTag
    import importlib.util

    
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'BadData.log')
    logging.basicConfig(filename = filename, level = logging.DEBUG, format='%(asctime)s %(message)s')
    #constants
    DATETIME = 'date' #the name of the column containing sampling datetime as a numeric
    DESCXML = 'Descriptor.xml' #the suffix of the xml for each component that contains max/min values
    COMPSEPERATOR = '' #the seperator between the component and suffix for each column name
    MAXINLINE = 4 #up to 5 records can have the same value recorded before we call these values bad.
 
    #pandas.Series -> Dataframe
    #returns a dataframe of start and stop indices for values that are repeated (inline).
    def isInline(x,maxinline):
        try:
            #x has a datetime index so we reset it to numerical, then use the datetime index as a column called 'index' so that we can pull the min max indices
            newx = x.reset_index().reset_index()
            newx.columns=['intind','index','val']
            
            inline = newx.groupby(newx.val.diff().ne(0).cumsum()).agg({'val':'first', 'index':['min','max']})
            inline.columns = inline.columns.droplevel(0)
            inline = inline.rename(columns={'first':'value','min':'start','max':'end'})
            #create a column that counts the number of rows that are inline
            inline['count'] = recordCount(data.fixed,inline)
            #we get rid of inline rows that are within the acceptable number of duplicates
            inline = inline[inline['count'] > maxinline]
            return inline
        except:
            return pd.DataFrame()
     def isOffLine(x,maxinline):
#        try:
            #x has a datetime index so we reset it to numerical, then use the datetime index as a column called 'index' so that we can pull the min max indices
        newx = x.reset_index().reset_index()
        newx.columns=['intind','index','val']
        
        inline = newx.groupby(newx.val.diff().cumsum()).agg({'val':'first', 'index':['min','max']})
        inline.columns = inline.columns.droplevel(0)
        inline = inline.rename(columns={'first':'value','min':'start','max':'end'})
        #create a column that counts the number of rows that are inline
        inline['count'] = recordCount(data.fixed,inline)
        #we get rid of inline rows that are within the acceptable number of duplicates
        inline = inline[inline['count'] > maxinline]
        return inline
#        except:
#            return pd.DataFrame()   
##    def isOffLine(df, window):
#        
#        var_frame = df.copy()
#        for column in df.columns:
#            ps= (df[column].diff() == 0) | (df[column].diff(-1) == 0)
#            var_frame[column] = ps              
#        var_frame['total_var'] = var_frame.sum(1)
#        var_frame['total_count'] = var_frame.count(1) - 1
#        offline = var_frame.total_var == var_frame.total_count
#        del var_frame
#        return offline

        
     #dataframe, dataframe -> list 
     #returns a list of the number of records in df between each indice provided in inline
    def recordCount(df, inline):
        counts = []
        for i in range(len(inline)):
            l = len(df.loc[inline.start.iloc[i]:inline.end.iloc[i]])
            counts.append(l)
        return counts
 
    
      #dataframe - datetime, pandas.Offset, string
      #returns the firs date to start searching, the range in duration to compare the distribtion to based on the characteristics of the missing block of data
    def getMoveAndSearch(missingBlock):
        #for large missing blocks of data we use a larger possible search range
        if (missingBlock.index.max(0) - missingBlock.index.min(0)) >= pd.Timedelta('1 days'):
            initial_years = 1
            initial_months = 2
            initial_days = 14
            search_range = pd.DateOffset(months =4)
        elif (missingBlock.index.max(0) - missingBlock.index.min(0)) <= pd.Timedelta('1 days'):
            initial_years = 1
            initial_months = 1
            initial_days = 14
            search_range = pd.DateOffset(weeks =8)
           
        search_start = missingBlock.index[0] - pd.DateOffset(years = initial_years, months = initial_months, days = initial_days)
        return search_start, search_range
  
     #datetime -> boolean
    #returns true if the datetime provided is a weekday
    def isWeekday(dt):       
        if dt.dayofweek <=5:
            return True
        else:
            return False  
    #String, DataFrame, Dictionary, DataFrame -> DataFrame, Dictionary
    #inline values are replaced and index is recorded in datadictionary
    def inlineFix(component, df, baddata,inline):  
        logging.debug("component is: %s",component)
        logging.debug(inline)
       
        #inline values are replaced
        print('Attempting to replace %d subsets for %s.' %(len(inline), component) )
        for l in inline.index.tolist():
            start_index = inline.start[l]
            end_index = inline.end[l]
            #inline values get changed to null first so they can't be used in linear interopolation
            df.loc[start_index:end_index,component] = None
            badDictAdd(component,
                     baddata,'2.Inline values',
                     df[pd.isnull(df[component])].index.tolist())
            
        #here is where we actually replace values.
        for l in inline.index.tolist():
            logging.info("inline index is %d", l)
            start_index = inline.start[l]
            end_index = inline.end[l]
            #attempt to replace using direct value transfer from similar data subset or linear interpolation
            getReplacement(df,component,start_index,end_index)  
        return df, baddata
   
        
    #dataframe, string, integer, integer -> dataframe
    #search for a subset of data to replace block of missing values that occurrs between start and stop indices.
    #if a suitable block of values is not identified linear interpolation is used.
    def getReplacement(df, component,start,stop):
         #this is a dataframe subset of our missing data
         missingBlock = df.loc[start:stop]
        
        #find the point we should start searching for matching data
        #this is the ideal spot and if we get a match we can stop searching        
         searchStart,searchRange = getMoveAndSearch(missingBlock) 
         currentYear = missingBlock.index[0].year
         evaluationYear = df.loc[searchStart:].index.year[0]
         first_valid = None
         #if there is a first valid the we can stop looking, ptherwise we increment our search window by a year
         while (first_valid == None) & (searchStart.year <= currentYear):
            #search start and stop are the indices of the block of data that may contain potential replacement data
            searchStop = searchStart + searchRange
            searchBlock = df.loc[searchStart:searchStop][component]
            #window is the number of missing records to fill
            window = len(df.loc[start:stop])
            duration = max(missingBlock.index) - min(missingBlock.index)
            comparison_block = df.loc[start - duration:stop + duration][component][df[component] != 0]
            #if there is any data in the search block we start comparing it to the distribution surrounding our missing data
            if len(searchBlock) > 0:
                #we get an array of whether or not a data block distribution matches
                ps= searchBlock.rolling(window).apply(lambda x: doMatch(x,comparison_block) ) 
                possibles = df.loc[ps[(ps >= 0.1)].index] 
                if len(possibles) > 0:
                    #we need to further evaluate whether the matching distributions also match the date time structure of our missing data
                    possibles['date']=possibles.index.to_datetime()
                    
                    #only weekdays should be matched with weekdays and weekends with weekends
                    possibles =possibles[possibles['date'].apply(isWeekday) == isWeekday(stop)]
                    possibles = possibles.drop('date',1)
                    #if our missing data spans less than 1 day then we need to match the time of day as well
                    if duration <= pd.Timedelta('1 days'):
                        #we want the hour to be within 3 hours of the actual missing values
                        possibles = possibles[abs(stop.hour -possibles.index.to_datetime().hour) <= 3]
                    #first valid is the index of the first data row that matches in distribution as well as day and time structure
                    first_valid = possibles.first_valid_index()
            #we bump our searching start point up by a year to continue searching if no valid value was found in the current search year. 
            searchStart = searchStart + pd.DateOffset(years = 1)
            
       
        #if we found a suitable block of values we insert them into the missing values otherwise we interpolate the missing values
         if first_valid != None:
            logging.info("replaced inline values %s through %s" %(str(min(missingBlock.index)), str(min(missingBlock.index))))
            #this is our replacement data
            replacement = df[df.index <= first_valid][0:window]
            #here we actually replace these data
            dataReplace(df,component, missingBlock, replacement)
         elif len(missingBlock) < 20:
           logging.info("No similar data subsets found. Using linear interpolation to replace inline values %s through %s" %(str(min(missingBlock.index)), str(min(missingBlock.index))))
           index_list = missingBlock.index.tolist()
           linearFix(index_list,df,component)
         else:
              logging.info("Could not replace missing values. Replace values for %s through %s manually" %(min(missingBlock.index),max(missingBlock.index)))

          
    #dataframe -> dataframe   
    #fills values for all components for time blocks when data collection was offline  
    def fixOfflineData(df,baddata):
      #find offline time blocks 
      inline = isInline(df['total_p'],2)
      #the value is the difference between records, so 0 indicates two records are the same. 
      inline = inline[inline.value == 0]
      df.total_p[df.total_p == 0] = None
      logging.debug('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (len(inline), len(df[pd.isnull(df.total_p) ])))
      #record the offline records in our baddata dictionary
      badDictAdd(component,
             baddata,'4.Offline',
             df[pd.isnull(df.total_p)].index.tolist())
      #here is where we actually replace values.
      for l in inline.index.tolist():
          
          start_index = inline.start.loc[l]
          end_index = inline.end.loc[l]
          #attempt to replace using direct value transfer from similar data subset or linear interpolation
          getReplacement(df,'total_p',start_index,end_index)  
      return 
        
    #dataframe, string, integer, integer, integer -> dataframe
    #replaces a subset of data in a series with another subset of data of the same length from the same series
    #if component is total_p then replaces all columns with replacement data
    def dataReplace(df,component, missing, replacement):
        if component == 'total_p':
            df.loc[min(missing.index):max(missing.index),] = replacement.values   
        else:
            df.loc[start:stop,component] = df[(replacement_last_i - (stop-start)).astype(int):(replacement_last_i + 1).astype(int)][component].values
        return df
        
    #string, dictionary, string, list of integers -> dictionary
    #adds a list of indices to a dictionary of bad values existing within a dataset.   
    def badDictAdd(component, current_dict, error_msg, index_list):
        #if the component exists add the new error message, otherwise start the component
        try:
            current_dict[component][error_msg]=index_list
        except KeyError:
            current_dict[component]= {error_msg:index_list}
            
    #numeric array, numeric array -> float       
    #returns the p value from the comparison of 2 distributions (x and y) using the Two-sample Kolmogorov-Smirnov Test
    def doMatch(x,y): 
       if len(x[pd.isnull(x)]) > 0:
           return 0
       else:
           m1 =  stats.ks_2samp(x,y)       
           return m1.pvalue
    #list of datetime, dataframe, component -> dataframe
    #modifies the existing values in a dataframe using linear interpolation        
    def linearFix(index_list, df,component):
         
         for i in index_list: 
             index = getIndex(df[component],i)   
             x = (pd.to_timedelta(pd.Series(df.index.to_datetime()))).dt.total_seconds().astype(int)
             x.index = pd.to_datetime(df.index)
             y = df[component]
                      
             value =  linearEstimate(x[[min(index), max(index)+ 1]],
                   y[[min(index),max(index)]], x.loc[i])
             df.loc[i, component]= value
             
         return df
    
    #panda.Series, datetime -> list of index
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
    #TODO get rid of slice warning
    #string, dataframe, dictionary -> dataframe, dictionary
    #changes netagive values to 0 for the specified component. Row indexes are stored in the baddata dictionary
    def negativeToZero(component,df,baddata):
           badDictAdd(component, baddata, '3.Negative value', df[df[component] < 0].index.tolist())
           df[component][df[component] < 0] = 0
           return df
       
   
     #dataframe, -> dataframe  
     #scales raw values to standardized units for model input
    def scaleData(df,ListOfComponents):
         for c in ListOfComponents:
             component = c.name.lower()
             if component[-1:] == 'p':
                componentAttributes = c.attribute
                useName = component
                componentUnits = c.units
                # convert units
                # cd to unit conventions file
                dir_path = os.path.dirname(os.path.realpath(__file__))
                unitConventionDir = dir_path +'..\\..\\GBSAnalyzer\\UnitConverters'
                # get the default unit for the data type
                units = readXmlTag('internalUnitDefault.xml', ['unitDefaults',componentAttributes], 'units', unitConventionDir)[0]
                # if the units don't match, convert
                if units.lower() != componentUnits.lower():
                    unitConvertDir = dir_path + '..\\..\\GBSAnalyzer\\UnitConverters\\unitConverters.py'
                    funcName = componentUnits.lower() + '2' + units.lower()
                    # load the conversion
                    spec = importlib.util.spec_from_file_location(funcName, unitConvertDir)
                    uc = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(uc)
                    x = getattr(uc, funcName)
                    # update data
                    df[useName] = x(df[useName])
                # get the scale and offset
                scale = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes], 'scale',
                                   unitConventionDir)[0]
                offset = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes], 'offset',
                               unitConventionDir)[0]
                df[useName] = df[useName]*int(scale) + int(offset)
                # get the desired data type and convert
                datatype = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes], 'datatype',
                                    unitConventionDir)
                
                if datatype[0][0:3] == 'int':
                    df[useName] = round(df[useName].astype('float'),0)
                else:  
                    df[useName] = df[useName].astype(datatype[0])
                 
    
    
    class Component:
         def __init__(self, component,units,attribute):
            self.name = component
            self.units = units
            self.attribute = attribute
            
     #DataClass is object with raw_data, fixed_data,baddata dictionary, and data summaries.
    class DataClass:
       """A class with access to both raw and fixed dataframes."""
       def __init__(self, raw_df):
            self.raw = raw_df
            self.fixed = pd.DataFrame(raw_df.copy(),raw_df.index,raw_df.columns)
            #give the fixed data a time index to work with
            time_index = pd.to_datetime(self.fixed.iloc[:,0], unit = 's')
            self.fixed.index = time_index
            self.fixed.columns = self.fixed.columns.str.lower()
            self.fixed = self.fixed.drop(DATETIME, axis =1 )
            
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
               axarr[i].plot(self.raw['DATE'],self.raw[components[i]])
               axarr[i].plot(self.fixed[DATETIME],self.fixed[components[i].lower()]);
               axarr[i].set_title(component)
          
           f.subplots_adjust(hspace=0.3)
           plt.show()
    #create DataClass object to store raw, fixed, and summery output 
    data = DataClass(df) 
    ListOfComponents = []
    for i in range(len(componentList)):
        x = Component(componentList[i],componentUnits[i],componentAttributes[i])
        ListOfComponents.append(x)
   
    #create a total power column. Total power is more important than indavidual components
    data.fixed['total_p'] = None
    #run through data checks for each component that is a power output component (ends in p)
    power_columns = []
    for c in ListOfComponents:
        component = c.name.lower()
        if component[-1:] == 'p':
            power_columns.append(component)
    #total power is the sum of values in all the power components        
    data.fixed['total_p'] = data.fixed[power_columns].sum(1)
    
    #identify when the entire system was offline - not collecting data.
    offline = isOffLine(data.fixed.total_p,3)
    for i in range(len(offline)):
          data.fixed.loc[offline.start.iloc[i]:offline.end.iloc[i]] = None

    #resum the total power. NA rows will sum to 0.
    data.fixed['total_p'] = data.fixed[power_columns].sum(1)
    #make a copy of these data before we scale them. We will need it to identify inline values.
    unscaled_copy = data.fixed.copy()
    #scale data
    scaleData(data.fixed, ListOfComponents)
    
    #now we replace the 0's with values from elsewhere in the dataset
    fixOfflineData(data.fixed,data.baddata)  

          
     for c in ListOfComponents:
        component = c.name.lower()
        if component[-1:] == 'p':
            descriptorxmlpath = os.path.join(setupDir,'..','Components',''.join([component[0:4],DESCXML]))      
            try:
                descriptorxml = ET.parse(descriptorxmlpath)
                
                try:
                     #make negative values 0
                     negativeToZero(component,data.fixed,data.baddata)
                     #find repeated values first for individual components before we scale these data
                     inline = isInline(unscaled_copy[component])
                     #fix inline values using scaled data
                     inlineFix(component,data.fixed,data.baddata,inline)
                    
                     #after replacing inline values replace values that are out of bounds
                     #out of bounds values are set to Nan first then linear interpolation is used.
                     checkMinMaxPower(component, data.fixed, descriptorxml,data.baddata)                 
                     linearFix(data.fixed[data.fixed[component].isnull()].index.tolist(),
                                         data.fixed,component) 
                    
                except KeyError:
                    print('no column named %s' %component)
            except FileNotFoundError:
                print ('Descriptor xml for %s not found' %component)
    data.fixed.insert(0,'date',data.fixed.index.to_datetime())    
    data.summarize()
    data.visualize(componentList)
    
    return data.fixed, data.baddata


