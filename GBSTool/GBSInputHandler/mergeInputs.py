# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 16:59:08 2018

@author: tcmorgan2
"""

import numpy as np
from GBSInputHandler.readDataFile import readDataFile
import pandas as pd
import functools
import operator

# CONSTANTS
YEARSECONDS = 31536000 # seconds in a non-leap Year
#reads input files and merges them into a single dataframe
#input dictionary must contain a fileLocation attribute, fileType, headerNames, newHeaderNames, componentUnits,
#Dictionary->DataFrame, List

def avg_datetime(series):
    dt_min = series.min()
    deltas = [x-dt_min for x in series]
    return dt_min + (series - dt_min).mean()

def mergeInputs(inputDictionary):

    # iterate through all sets of input files
    for idx in range(len(inputDictionary['fileLocation'])):
        df0, listOfComponents0 = readDataFile(inputDictionary['fileType'][idx],inputDictionary['fileLocation'][idx],inputDictionary['fileType'][idx],
                                             inputDictionary['headerNames'][idx],inputDictionary['newHeaderNames'][idx],inputDictionary['componentUnits'][idx],
                                             inputDictionary['componentAttributes'][idx], 
                                             inputDictionary['dateColumnName'][idx], inputDictionary['dateColumnFormat'][idx], 
                                             inputDictionary['timeColumnName'][idx], inputDictionary['timeColumnFormat'][idx], 
                                             inputDictionary['utcOffsetValue'][idx], inputDictionary['utcOffsetUnit'][0], 
                                             inputDictionary['dst'][idx]) # dataframe with time series information. replace header names with column names
        if idx == 0: # initiate data frames if first iteration, otherwise append
            df = df0
            listOfComponents = listOfComponents0
        else:
            # the following code overlaps time series data, which does not necessarily line up, since from diff years
            # this causes jumps in the time series
            '''
            # check if on average more than a year difference between new dataset and existing
            meanTimeNew = avg_datetime(df0.DATE)
            meanTimeOld = avg_datetime(df.DATE)
            # round to the nearest number of year difference
            yearDiff = np.round((meanTimeNew - meanTimeOld).days/365)
            # if the difference is greater than a year between datasets to be merged, see if can change the year on one
            if abs(yearDiff) >= 0:
                # if can change the year on the new data
                if inputDictionary['flexibleYear'][idx]:
                    # find the number of years to add or subtract
                    df0.DATE = df0.DATE - pd.to_timedelta(yearDiff, unit='y')
                # otherwise, check if can adjust the existing dataframe
                elif all(inputDictionary['flexibleYear'][:idx]):
                    df.DATE = df.DATE + pd.to_timedelta(yearDiff, unit='y')
            '''
            df = df.append(df0)
            listOfComponents.extend(listOfComponents0)
    
    # order by datetime
    df = df.sort_values(['DATE']).reset_index(drop=True)
    # find rows with identical dates and combine rows, keeping real data and discarding nans in columns
    dupDate = df.DATE[df.DATE.duplicated()]
    
    for date in dupDate: # for each duplicate row
        # find with same index
        sameIdx = df.index[df.DATE == date]
        # for each column, find first non-nan value, if one
        for col in df.columns:
            # first good value
            goodIdx = df.loc[sameIdx,col].first_valid_index()
            if goodIdx != None:
                df.loc[sameIdx[0], col]= df.loc[goodIdx, col]
        # remove duplicate columns
        df = df.drop(sameIdx[1:])
     # remove duplicates in list of components - can't have columns of the same name in the dataframe  
     
    def uniqueList(startList,outList):
        if len(startList) <= 0:
            return outList
        else:
            if startList[0].column_name not in [n.column_name for n in outList]:
                outList.append(startList[0])
            return uniqueList(startList[1:],outList)
        
    l = uniqueList(listOfComponents,[])
    
    return df, l