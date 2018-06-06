# DataClass is object with raw_data, fixed_data,baddata dictionary, and system characteristics.
from GBSTool.GBSInputHandler.identifyGenColumns import identifyGenColumns
import pandas as pd
from GBSTool.GBSInputHandler.isInline import isInline
from GBSTool.GBSInputHandler.badDictAdd import badDictAdd
from GBSTool.GBSInputHandler.getReplacements import getReplacement
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
            self.fixed = self.splitDataFrame(pd.DataFrame(raw_df.copy(), raw_df.index, raw_df.columns),maxMissing)
            print('Created %d dataframes that will be evaluated.' %len(self.fixed))
            # give the fixed data a time index to work with - assumes this is in the first column
            time_index = pd.to_datetime(self.fixed.iloc[:, 0], unit='s')

            self.fixed = self.fixed.drop(self.fixed.columns[0], axis=1)
            self.fixed.index = time_index
        else:
            self.raw = pd.DataFrame()
            self.fixed = pd.DataFrame()
        self.timeInterval = sampleInterval
        self.powerComponents = []
        self.ecolumns = []
        #truncate is a list of dates that indicate the portion of the dataframe to fix and include in analysis
        self.truncate = truncate
        self.maxmissing = maxmissing
        self.baddata = {}
        return
    def getattribute(self, a):
        return self.__getattribute__(a)
    
    #DataFrame, timedelta ->listOfDataFrame
    #splits a dataframe where data is missing that exceeds maxMissing
    def splitDataFrame(self,df, m):
        df = df.sort_index(0, ascending=True)
        df['timeDiff'] = pd.Series(pd.to_datetime(df.index, unit='s'), df.index).diff()
        df['gaps'] = df['timeDiff'].apply(lambda x: 1 if x > pd.to_timedelta(m) else 0).cumsum()
        #these are the dataframe groups
        groups = df.groupby('gaps',as_index=True)
        d=[]
        for name, group in groups:
            group = group.drop('gaps', axis = 1)
            group = group.drop('timeDiff', axis = 1)
            d.append(group)
        return d
    
    # DataClass -> null
    # summarizes raw and fixed data and print resulting dataframe descriptions
    def summarize(self):
        '''prints basic statistics describing raw and fixed data'''
        print('raw input summary: ')
        print(self.raw.describe())
        print('fixed output summary: ')
        print(self.fixed.describe())
        return

    # list -> null
    # identifies when there are no generator values
    # if the system can't operate withouth the generators (GEN = True) then values are filled
    # with data from a matching time of day (same as offline values)
    def fixGen(self, componentList):
        gencolumns = identifyGenColumns(componentList)
        self.fixed['gentotal'] = self.fixed[gencolumns].sum(1)
        self.fixed['grouping'] = isInline(self.fixed['gentotal'])
        groups = self.fixed.groupby(self.fixed['grouping'], as_index=True)

        logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (
            len(groups), len(self.fixed[pd.isnull(self.fixed.total_p)])))
        # record the offline records in our baddata dictionary
        badDictAdd('gen',
                   self.baddata, '2.Generator offline',
                   self.fixed[self.fixed.gentotal==0].index.tolist())

        self.fixed.gentotal.replace(0, np.nan)
        for name, group in groups:
            if min(group.gentotal) == 0:
                getReplacement(self.fixed, group.index, gencolumns)

        self.fixed = self.fixed.drop('gentotal', 1)
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
            plt.plot(self.fixed.index, self.fixed[TOTALP], 'b-')
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
        timeDiff = pd.Series(pd.to_datetime(self.fixed.index, unit='s'), self.fixed.index).diff()
        timeDiff = timeDiff.sort_index(0, ascending=True)
        timeDiff = timeDiff[timeDiff > 2 * pd.to_timedelta(self.timeInterval)]
        # fill the gaps with NA
        for i in timeDiff.index:
            resample_df = self.fixed.loc[:i][-2:]
            resample_df = resample_df.resample(self.timeInterval).mean()
            self.fixed = self.fixed.append(resample_df[:-1])
            self.fixed = self.fixed.sort_index(0, ascending=True)
        return

    # Dataclass -> null
    # sums the power columns into a single column
    def totalPower(self):
        self.fixed[TOTALP] = self.fixed[self.powerComponents].sum(1)
        self.raw[TOTALP] = self.raw[self.powerComponents].sum(1)
        return

    # List of Components -> null
    # scales raw values to standardized units for model input
    def scaleData(self, ListOfComponents):
        for c in ListOfComponents:
            c.setDatatype(self.fixed)
        return

    # DataClass -> null
    # replaces time interval data where the power output drops or increases significantly
    # compared to overall data characteristics
    def removeAnomolies(self, stdNum = 3):
        # stdNum is defines how many stds from the mean is acceptable. default is 3, but this may be too tight for some data sets.
        mean = np.mean(self.fixed[TOTALP])
        std = np.std(self.fixed[TOTALP])
        #self.fixed[(self.fixed[TOTALP] < mean - 3 * std)] = None
        self.fixed[(self.fixed[TOTALP] < mean - stdNum * std) | (self.fixed[TOTALP] > mean + stdNum * std)] = None
        # replace values with linear interpolation from surrounding values
        self.fixed = self.fixed.interpolate()
        self.totalPower()
        return
###########
        
    # DataClass -> null
    # fills values for all components for time blocks when data collection was offline
    # power components are summed and replaced together
    # ecolumns are replaced individually
    def fixOfflineData(self):
        # find offline time blocks
        groups = self.fixed.groupby(self.fixed['grouping'], as_index=True)

        logging.info('%d blocks of time consisting of %d rows of data are offline and are being replaced' % (
            len(groups), len(self.fixed[pd.isnull(self.fixed.total_p)])))
        # record the offline records in our baddata dictionary
        badDictAdd(TOTALP,
                   self.baddata, '2.Offline',
                   self.fixed[pd.isnull(self.fixed[TOTALP])].index.tolist())

        self.fixed[TOTALP].replace(0, None)
        # based on our list of bad groups of data, replace the values
        for name, group in groups:
            if (len(group) > 3) | (min(group[TOTALP]) == 0):
                getReplacement(self.fixed, group.index, 'total_p')
        return
