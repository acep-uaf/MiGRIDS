# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:42:42 2018

@author: jbvandermeer
"""

# imports
import sys
import os
import tkinter as tk
from tkinter import filedialog

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile
from GBSModel.getSeriesIndices import getSeriesIndices
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import pandas as pd
import itertools



def plotProjectSet(projectSetDir=''):
    if projectSetDir == '':
        print('Choose the directory for the set of simulations')
        root = tk.Tk()
        root.withdraw()
        projectSetDir = filedialog.askdirectory()

    # get the run number
    dirName = os.path.basename(projectSetDir)
    try:
        setNum = int(dirName[3:])
    except ValueError:
        print(
            'The directory name for the simulation set results does not have the correct format. It needs to be \'Setx\' where x is the run number.')


    # load the results dataframe
    os.chdir(projectSetDir)
    conn = sqlite3.connect('set' + str(setNum) + 'Results.db')
    # check if Results table exists, tableName will be empty if not
    tableName = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name='Results';", conn)
    # if not initialized
    if tableName.empty:
        print('No results have been calculated for this set yet.')
        return # exit function
    else:
        dfRes = pd.read_sql_query('select * from Results', conn)
    conn.close()

    # load the simulation parameters for each run
    os.chdir(projectSetDir)
    conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db')
    # check if Results compAttr exists, tableName will be empty if not
    tableName = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name='compAttributes';", conn)
    # if not initialized
    if tableName.empty:
        print('This simulation set has not been set up yet.')
        return  # exit function
    else:
        dfAttr = pd.read_sql_query('select * from compAttributes', conn)
    conn.close()

    # plot diesel output vs each attribute
    columns = list(dfAttr.columns.values)

    for col in columns:
        # make sure indices in order for x and y
        x = dfAttr[col]
        y = dfRes['Generator Import kWh']
        # group according to other columns
        otherColumns = columns.copy()
        otherColumns.remove(col)
        legendValues = []
        legendNames = []
        legendIndices = []
        for otherCol in otherColumns:
            if any(dfAttr[otherCol] != dfAttr[col]) and otherCol.lower() != 'started': # make sure not identical (this is an option when setting values of 2 different attributes
                legendNames.append(otherCol) # add col name to legend names
                uniqueValues = np.unique(dfAttr[otherCol]) # unique values of this column
                legendValues.append(list(uniqueValues)) # add the value that correspond to the legend name
                # get indices of unique values
                indVal = []
                for uniqueVal in uniqueValues:
                    indVal.append(dfAttr.index[dfAttr[otherCol]==uniqueVal].tolist())
                legendIndices.append(indVal)

        # find common indices for each combination of other columm values
        possibleCombValues = list(itertools.product(*legendValues))
        possibleCombIndices = list(itertools.product(*legendIndices))

        # get the intersection of indices for each legend grouping
        possibleCombIndicesIntersection = []
        legendText = []
        for idx, indComb in enumerate(possibleCombIndices): # for each combination of values
            possibleCombIndicesIntersection.append(set.intersection(*map(set, indComb)))
            legStr = ''
            for idx0, name in enumerate(legendNames):
                legStr = legStr + name + ': ' + str(possibleCombValues[idx][idx0]) + ' '

            legendText.append(legStr)

        # plot each line
        plt.figure()
        for idx, combIdx in enumerate(possibleCombIndicesIntersection):
            xIdx = list(combIdx) # the indicies for x
            yIdx = [y.index[i] for i in combIdx]
            xPlot = x.loc[combIdx]
            yPlot = y.loc[combIdx]
            idxSort = np.argsort(xPlot).tolist()
            # the indicies for y
            # sort x
            idxSort =  np.argsort(x[xIdx]).tolist()
            plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort], '-*')

        plt.ylabel('kWh')
        plt.title('Diesel geneator output')
        #TODO: grab x label values from component descriptor, or..?
        plt.xlabel('')
        plt.legend(legendText)
        plt.show()
        plt.savefig('genOutputVs'+ col +'.png')

        # save a csv file
        dfAttrRes = pd.concat([dfAttr,dfRes],join_axes=1)
        dfAttrRes.to_csv('Set' + str(setNum) + 'AttributesResults.csv')

    input('Press enter to close figures. ')


