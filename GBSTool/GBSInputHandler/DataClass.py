# DataClass is object with raw_data, fixed_data,baddata dictionary, and system characteristics.
from GBSInputHandler.identifyGenColumns import identifyGenColumns
import pandas as pd
from GBSInputHandler.isInline import *
from GBSInputHandler.badDictAdd import badDictAdd
#from GBSInputHandler.getReplacements import getReplacement
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib as plt
import pickle
import numpy as np
import os
import logging

TOTALP = 'total_p'
MAXMISSING= '14 days'

class DataClass:
    """A class with access to both raw and fixed dataframes."""
    #DataFrame, timedelta,list,timedelta -> 
    def __init__(self, raw_df, sampleInterval,runTimeSteps=None,maxMissing=MAXMISSING):
        if len(raw_df) > 0:
            self.raw = raw_df.copy()
             
            #self.fixed is a list of dataframes derived from raw_df split whenever a gap in data greater than maxmissing occurs           
            self.fixed = []
            #df is a single dataframe converted from raw_df
            #once cleaned and split into relevent dataframes it will become fixed
            self.df = pd.DataFrame(raw_df.copy(), raw_df.index, raw_df.columns)
            self.df[TOTALP] = np.nan
            # all dataframes passed from readData will have a datetime column named DATE
            for c,df in enumerate(self.fixed):
                if 'DATE' in df.columns:
                    df.index = pd.to_datetime(df['DATE'], unit='s')
                    df = df.drop('DATE', axis=1)
                
                self.fixed[c] = df
        else:
            self.raw = pd.DataFrame()
            self.rawCopy = pd.DataFrame()
            self.fixed = [pd.DataFrame()]
        
        self.timeInterval = sampleInterval
        self.powerComponents = []
        self.ecolumns = []
        #runTimeSteps is a list of dates that indicate the portion of the dataframe to fix and include in analysis
        self.runTimeSteps = runTimeSteps
        self.maxMissing = maxMissing
        self.baddata = {}
        return
    def getattribute(self, a):
        return self.__getattribute__(a)
    
    #DataFrame, timedelta ->listOfDataFrame
    #splits a dataframe where data is missing that exceeds maxMissing
    def splitDataFrame(self):
       self.fixed = [self.df]
       #dataframe splits only occurr for total_p, individual load columns
       self.fixed = cutUpDataFrame(self.fixed, [TOTALP] + self.loads)
       
    # DataClass -> null
    # summarizes raw and fixed data and print resulting dataframe descriptions
    def summarize(self):
        '''prints basic statistics describing raw and fixed data'''
        print('raw input summary: ')
        print(self.raw.describe())
        print('fixed output summary: ')
        #each seperate dataframe gets described
        print([d.describe() for d in self.fixed])
        return

    # list -> null
    # identifies when there are no generator values
    # if the system can't operate withouth the generators (GEN = True) then values are filled
    # with data from a matching time of day (same as offline values)
    def fixGen(self, componentList):
        gencolumns = identifyGenColumns(componentList)
        if len(gencolumns) > 0:
            df_to_fix = self.df.copy()
            
            df_to_fix['hasData'] = (pd.notnull(df_to_fix[gencolumns])).sum(axis=1)
            df_to_fix = df_to_fix[df_to_fix['hasData'] >= 1]
            df_to_fix['gentotal'] = df_to_fix[gencolumns].sum(1)
            
            #group values that repeat over sampling intervals 
            grouping =df_to_fix[df_to_fix['gentotal']==0]['gentotal']
            grouping = pd.notnull(grouping).cumsum()
            if len(grouping[pd.notnull(grouping)]) > 0:
               reps = self.fixOfflineData(gencolumns,grouping)
               self.df = self.df.drop(reps.columns, axis=1)
               self.df= pd.concat([self.df,reps],axis=1)   
     
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
            #plot all the fixed dataframes together
            plt.plot(pd.concat(self.fixed).index, pd.concat(self.fixed)[TOTALP], 'b-')
            plt.title('Fixed data total power')
            pdf.savefig()
            plt.close()

    # DataClass string -> pickle
    # pickles the dataframe so it can be restored later
    def preserve(self, setupDir):
        filename = os.path.join(setupDir + '/../TimeSeriesData', 'fixed_data.pickle')
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        pickle_out = open(filename, 'wb')
        pickle.dump(self.fixed, pickle_out)
        pickle_out.close
        return

    # DataClass->null

    # Dataclass -> null
    # sums the power columns into a single column
    def totalPower(self):  
        self.df[TOTALP] = self.df[self.powerComponents].sum(1)
        self.df[TOTALP] = self.df[TOTALP].replace(0,np.nan)
        self.raw[TOTALP] = self.raw[self.powerComponents].sum(1)
        return

    # List of Components -> null
    # scales raw values to standardized units for model input
    def scaleData(self, ListOfComponents):
        for c in ListOfComponents:
           c.setDatatype(self.df)
        return

    # DataClass -> null
    # replaces time interval data where the power output drops or increases significantly
    # compared to overall data characteristics
    def removeAnomolies(self, stdNum = 3):
        # stdNum is defines how many stds from the mean is acceptable. default is 3, but this may be too tight for some data sets.
        mean = np.mean(self.df[TOTALP])
        std = np.std(self.df[TOTALP])
    
        self.df[(self.df[TOTALP] < mean - stdNum * std) | (self.df[TOTALP] > mean + stdNum * std)] = None
         # replace values with linear interpolation from surrounding values
        self.df = self.df.interpolate()
        self.totalPower()
        return
    
    def setYearBreakdown(self):
        self.yearBreakdown = yearlyBreakdown(self.df)
        return

    # fills values for all components for time blocks when data collection was offline
    # power components are summed and replaced together
    # load columns are replaced individually
    # ecolumns are replaced individually
    def fixOfflineData(self,columnsToReplace,groupingColumn):
        #try quick replace first
        column = columnsToReplace[0]
        df = self.df[columnsToReplace].copy()
        original_range = [df.first_valid_index(),df.last_valid_index()]
        RcolumnsToReplace = ['R' + c for c in columnsToReplace]
        notReplacedGroups   = groupingColumn
        for g in range(len(self.yearBreakdown)):
            subS = df.loc[self.yearBreakdown.iloc[g]['first']:self.yearBreakdown.iloc[g]['last']]
            replacementS, notReplacedGroups = quickReplace(pd.DataFrame(df), subS, self.yearBreakdown.iloc[g]['offset'],notReplacedGroups)
            
            df = pd.concat([df, replacementS.add_prefix('R')],axis=1, join = 'outer')
            
            df.loc[((pd.notnull(df['R' + column])) &
                   (df.index >= min(subS.index)) &
                   (df.index <= max(subS.index))),columnsToReplace] = df.loc[((pd.notnull(df['R' + column])) &
                   (df.index >= min(subS.index)) &
                   (df.index <= max(subS.index))),RcolumnsToReplace].values      
            df = df.drop(RcolumnsToReplace, axis=1)

        groupingColumn.name = '_'.join([column,'grouping'])
        df_to_fix = pd.concat([df,groupingColumn],axis=1,join='outer')
        df_to_fix = df_to_fix[original_range[0]:original_range[1]]
        
        #df_to_fix is the dataset that gets filled in (out of bands records are excluded)
        if self.runTimeSteps is not None:
            df_to_fix = df_to_fix.loc[self.runTimeSteps[0]:self.runTimeSteps[1]]
         
        #if there is still data in the dataframe after we have truncated it 
        # to the specified interval replace bad data
        if len(df_to_fix) > 1:
            
            #remove groups that were replaced
            # find offline time blocks
            #get groups based on column specific grouping column
            groups = pd.Series(pd.to_datetime(df_to_fix.index),index=df_to_fix.index).groupby(df_to_fix['_'.join([column,'grouping'])]).agg(['first','last'])
            groups['size'] = groups['last']-groups['first']
            
            #filter groups we replaced already from the grouping column
            groups= groups[(groups['size'] > pd.Timedelta(days=1)) | 
                    groups.index.isin(notReplacedGroups[pd.notnull(notReplacedGroups)].index.tolist())]
            cuts = groups['size'].quantile([0.25, 0.5, 0.75,1])
            cuts = list(set(cuts.tolist()))
            cuts.sort()
            print("%s groups of missing or inline data discovered for component named %s" %(len(groups), column) )  
        df_to_fix = doReplaceData(groups, df_to_fix.loc[pd.notnull(df_to_fix[column])], cuts,df.loc[pd.notnull(df[column])])       
        
        return df_to_fix.loc[pd.notnull(df_to_fix[column]),columnsToReplace]    
     
    
   #DataFrame, String -> Boolean
   #return true if a column does not contain any values
    def isempty(self, df,column):
        if sum(df[column]) == 0:
            return True
        return False
    
    def truncateDate(self):
        if self.runTimeSteps is not None:
            for i,df in enumerate(self.fixed):
                df = df[self.runTimeSteps[0]:self.runTimeSteps[1]]
                if len(df) < 1:
                    self.fixed.remove(df)
                else:
                    self.fixed[i] = df