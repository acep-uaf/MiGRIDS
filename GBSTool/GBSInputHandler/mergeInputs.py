# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 16:59:08 2018

@author: tcmorgan2
"""

import numpy as np
from GBSInputHandler.readDataFile import readDataFile
import pandas as pd


# CONSTANTS
YEARSECONDS = 31536000 # seconds in a non-leap Year
#reads input files and merges them into a single dataframe
#input dictionary must contain a fileLocation attribute, fileType, headerNames, newHeaderNames, componentUnits,
#Dictionary->DataFrame, List

def avg_datetime(series):
    dt_min = series.min()
    return dt_min + (series - dt_min).mean()

def mergeInputs(inputDictionary):

    # iterate through all sets of input files
    for idx in range(len(inputDictionary['fileLocation'])):
        
        df0, listOfComponents0 = readDataFile(singleLocation(inputDictionary,idx))

        # set index as DATE
        df0.drop_duplicates('DATE', inplace=True)
        df0.set_index('DATE', inplace=True)

        if idx == 0: # initiate data frames if first iteration, otherwise append
            df = df0
            listOfComponents = listOfComponents0
        else:
            # the following code overlaps time series data, which does not necessarily line up, since from diff years
            # this causes jumps in the time series


            # concat, so that duplicate rows are combined and duplicate columns remain seperate
            df = pd.concat([df, df0], axis=1, join='outer')
            listOfComponents.extend(listOfComponents0)
    
    # order by datetime
    # merge duplicate columns
    # get all column names
    allCol = np.array(df.columns)
    allCol.dtype = 'object'  # if headers all single characters, it will cause replace col to fail later becuase of data type
    # get duplicate columns
    dupCol = []
    for col in allCol:
        if (len(np.where(allCol == col)[0]) > 1) & (col not in dupCol):
            dupCol = dupCol + [col]

    # dupCol = allCol[allCol.duplicated()] # this will have multiples of duplicate columns if more than 3

    for dc in dupCol:  # for each column with the same name
        # fill in first duplicate column with first non nan value
        df[dc] = df[dc].bfill(axis=1)

        # remove duplicate columns, keeping the first one
        # find all columns named this
        dcIdx = np.where(allCol == dc)[0]
        # rename columns
        allCol[dcIdx[1:]] = 'RemoveCol'
        df.columns = allCol
        df.drop('RemoveCol', axis=1, inplace=True)
        allCol = np.array(df.columns)
        allCol.dtype = 'object'

    def uniqueList(startList,outList):
        if len(startList) <= 0:
            return outList
        else:
            if startList[0].column_name not in [n.column_name for n in outList]:
                outList.append(startList[0])
            return uniqueList(startList[1:],outList)
        
    l = uniqueList(listOfComponents,[])


    #TODO update progress bar here
    return df, l

def singleLocation(dict, position):
    '''returns a dictionary that is a subset of the input dictionary with all the keys but only values at a specified position'''
    singleValueDict={}
    for key, val in dict.items():
        try:
            singleValueDict[key]=val[position]
        except IndexError:
            singleValueDict[key] =val[0]
    return singleValueDict