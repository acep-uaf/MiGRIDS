# DataClass is object with raw_data, fixed_data,baddata dictionary, and system characteristics.
from GBSInputHandler.identifyGenColumns import identifyGenColumns
import pandas as pd
from GBSInputHandler.isInline import isInline
from GBSInputHandler.badDictAdd import badDictAdd
from GBSInputHandler.getReplacements import getReplacement
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
    def __init__(self, raw_df, sampleInterval,truncate=None,maxMissing=MAXMISSING):
        if len(raw_df) > 0:
            self.raw = raw_df.copy()
             
            #self.fixed is a list of dataframes derived from raw_df split whenever a gap in data greater than maxmissing occurs           
            self.fixed = [pd.DataFrame(raw_df.copy(), raw_df.index, raw_df.columns)]
            
            # all dataframes passed from readData will have a datetime column named DATE
            for c,df in enumerate(self.fixed):
                df.index = pd.to_datetime(df['DATE'], unit='s')
                df = df.drop('DATE', axis=1)
                
                self.fixed[c] = df
        else:
            self.raw = pd.DataFrame()
            self.rawCopy = pd.DataFrame()
            self.fixed = [pd.DataFrame()]
        print(self.fixed[0].head())
        self.timeInterval = sampleInterval
        self.powerComponents = []
        self.ecolumns = []
        #truncate is a list of dates that indicate the portion of the dataframe to fix and include in analysis
        self.truncate = truncate
        self.maxMissing = maxMissing
        self.baddata = {}
        return
    def getattribute(self, a):
        return self.__getattribute__(a)
    
    #DataFrame, timedelta ->listOfDataFrame
    #splits a dataframe where data is missing that exceeds maxMissing
    def splitDataFrame(self, indices):
        newlist = []
        for df in self.fixed:
            df1 = df[:min(indices)]
            df2 = df[max(indices):]
            if len(df1) > 0:
                newlist.append(df1)
            if len(df2) > 0:
                newlist.append(df2)
        self.fixed = newlist
        return
    
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
        for df in self.fixed:
            df['gentotal'] = df[gencolumns].sum(1)
            df['grouping'] = isInline(df['gentotal'])
            groups = df.groupby(df['grouping'], as_index=True)
    
            logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (
                len(groups), len(df[pd.isnull(df.total_p)])))
            # record the offline records in our baddata dictionary
            badDictAdd('gen',
                       self.baddata, '2.Generator offline',
                       df[df.gentotal==0].index.tolist())
    
            df.gentotal.replace(0, np.nan)
            for name, group in groups:
                if min(group.gentotal) == 0:
                    getReplacement(self.fixed, group.index, gencolumns)
    
            df = df.drop('gentotal', 1)
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
        filename = os.path.join(setupDir + '../TimeSeriesData', 'fixed_data.pickle')
        pickle_out = open(filename, 'wb')
        pickle.dump(self.fixed, pickle_out)
        pickle_out.close
        return

    # DataClass->null
    # fills in records at specified time interval where no data exists.
    # new records will have NA for values
    def checkDataGaps(self):
        for df in self.fixed:
            timeDiff = pd.Series(pd.to_datetime(df.index, unit='s'), df.index).diff()
            timeDiff = timeDiff.sort_index(0, ascending=True)
            timeDiff = timeDiff[timeDiff > 2 * pd.to_timedelta(self.timeInterval)]
            # fill the gaps with NA
            for i in timeDiff.index:
                resample_df = df.loc[:i][-2:]
                resample_df = resample_df.resample(self.timeInterval).mean()
                df = df.append(resample_df[:-1])
                df = df.sort_index(0, ascending=True)
        return

    # Dataclass -> null
    # sums the power columns into a single column
    def totalPower(self):
        for df in self.fixed:
            df[TOTALP] = df[self.powerComponents].sum(1)
        self.raw[TOTALP] = self.raw[self.powerComponents].sum(1)
        return

    # List of Components -> null
    # scales raw values to standardized units for model input
    def scaleData(self, ListOfComponents):
        for c in ListOfComponents:
            for df in self.fixed:
                c.setDatatype(df)
        return

    # DataClass -> null
    # replaces time interval data where the power output drops or increases significantly
    # compared to overall data characteristics
    def removeAnomolies(self, stdNum = 3):
        # stdNum is defines how many stds from the mean is acceptable. default is 3, but this may be too tight for some data sets.
       for df in self.fixed:
            mean = np.mean(df[TOTALP])
            std = np.std(df[TOTALP])
        
            df[(df[TOTALP] < mean - stdNum * std) | (df[TOTALP] > mean + stdNum * std)] = None
             # replace values with linear interpolation from surrounding values
            df = df.interpolate()
       self.totalPower()
       return

    # DataClass -> null
    # fills values for all components for time blocks when data collection was offline
    # power components are summed and replaced together
    # load columns are replaced individually
    # ecolumns are replaced individually
    def fixOfflineData(self,column):
        for df in self.fixed:
            #df_to_fix is the dataset that gets filled in (out of bands records are excluded)
            if self.truncate is not None:
                df_to_fix = df[self.truncate[0]:self.truncate[1]]
            else:
                df_to_fix = df
            #if there is still data in the dataframe after we have truncated it 
            # to the specified interval replace bad data
            if len(df_to_fix) > 1:
                # find offline time blocks
                #if we are working with totalp gets grouped by totalp
                if column == TOTALP:
                    groups = df.groupby(df['grouping'], as_index=True)
                else:
                    #otherwise groups represent grouping for a specific columns
                    groups = df.groupby(df['_'.join([column,'grouping'])], as_index=True)
    
                logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (
                    len(groups), len(df[pd.isnull(df[column])])))
                # record the offline records in our baddata dictionary
                badDictAdd(column,
                       self.baddata, '2.Offline',
                       df[pd.isnull(df[column])].index.tolist())
                #replace the bad data values with None
                df[column].replace(-99999, None)
                # based on our list of bad groups of data, replace the values
                for name, group in groups:
                    if (len(group) > 3) | (min(group[column]) < 0):
                        #replacements can come from all of the input data not just the
                        #subsetted portion
                        #if no replacement and duration is longer than MAXMISSING False is returned
                        try:
                            self.dataReplace(getReplacement(pd.concat(self.fixed), group.index, column))
                            # a type error is returned if getReplacement returns False)
                        except (TypeError):
                            self.splitDataFrame(group.index)
        return

    # dataframe, dataframe, dataframe, string -> dataframe
    # replaces a subset of data in a series with another subset of data of the same length from the same series
    # if component is total_p then replaces all columns with replacement data
    def dataReplace(self, df, missing, replacement, component=None):
        '''replaces the values in one dataframe with those from another'''
        
        #if ecolumns are empty they will get replaced along with power components, otherwise they will remain as they were.
        if component == TOTALP:
            columnsToReplace = self.powerComponents 
            #only replace environment columns if there is no data in them
            for e in self.ecolumns:
                if self.isempty(e):
                    columnsToReplace.append(e)
        else:
            columnsToReplace = component
        df = df.join(replacement, how = 'outer',left_index = True, right_index=True, suffixes=('','replacement'))
        df.loc[min(missing.index):max(missing.index), columnsToReplace] = df.loc[min(missing.index):max(missing.index),['replacement'.join(c) for c in columnsToReplace]]
        
        return df
    
   #DataFrame, String -> Boolean
   #return true if a column does not contain any values
    def isempty(self, df,column):
        if sum(df[column]) == 0:
            return True
        return False
    
    def truncateDate(self):
        if self.truncate is not None:
            for df in self.fixed:
                df = df[self.truncate[0]:self.truncate[1]]
                if len(df) < 1:
                    self.fixed.remove(df)