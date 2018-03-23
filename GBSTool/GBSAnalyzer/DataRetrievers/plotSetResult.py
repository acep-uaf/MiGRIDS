#imports
import numpy as np
import os
import sqlite3
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import itertools
import matplotlib.pyplot as plt

def plotSetResult(plotRes,plotAttr, projectSetDir = '', otherAttr = '',otherAttrVal = ''):
    '''
    plot a single result for a set of simulations
    :param plotRes: the database column header of the variable to plot.
    :param plotAttr: The simulation attribute to be plotted against. This is the column header in the database as well as the tag and attribute from the component or setup xml file.
    :param otherAttr: The other component or setup attributes to have fixed values in the plot. If not specified, all values for the attribute will be plotted as multiple lines.
    :param otherAttrVal: The values of the 'otherAttr' to plot.
    :return: Nothing
    '''
    if projectSetDir == '':
        print('Choose the directory for the set of simulations')
        root = tk.Tk()
        root.withdraw()
        projectSetDir = filedialog.askdirectory()

    # get the set number
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
        return  # exit function
    else:
        dfRes = pd.read_sql_query('select * from Results', conn)
    conn.close()

    # load the simulation parameters for each run
    os.chdir(projectSetDir)
    conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db')
    # check if Results compAttr exists, tableName will be empty if not
    tableName = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name='compAttributes';",
                                  conn)
    # if not initialized
    if tableName.empty:
        print('This simulation set has not been set up yet.')
        return  # exit function
    else:
        dfAttr = pd.read_sql_query('select * from compAttributes', conn)
    conn.close()

    # remove values from otherAttr not to be plotted
    for idx, attr in enumerate(otherAttr):  # for set of values to plot for this attribute
        values = otherAttrVal[idx].split(',')
        # convert to numeric
        values = [float(x) for x in values]
        # go through each value for this attribute, check if it is in the list of values to plot, if not, remove row
        # from both dfAttr and dfRes
        dropIdx = []  # df indicies to drop
        for idx, attrVal in enumerate(dfAttr[attr]):
            if not float(attrVal) in values:
                # get the index of the row to be dropped and remove from both df
                dropIdx.append(dfAttr.index[idx])
                # dfAttr = dfAttr.drop(dfIdx)
                # dfRes = dfRes.drop(dfIdx)
        dfAttr = dfAttr.drop(dropIdx)
        dfRes = dfRes.drop(dropIdx)

    # get the names of all results columns
    columns = list(dfAttr.columns.values)

    x = dfAttr[plotAttr]
    y = dfRes[plotRes]
    # group according to other columns
    otherColumns = columns.copy()
    otherColumns.remove(plotAttr)
    legendValues = []
    legendNames = []
    legendIndices = []
    for otherCol in otherColumns:
        if any(dfAttr[otherCol] != dfAttr[plotAttr]) and otherCol.lower() != 'started':  # make sure not identical (this is an option when setting values of 2 different attributes
            legendNames.append(otherCol)  # add col name to legend names
            uniqueValues = np.unique(dfAttr[otherCol])  # unique values of this column
            legendValues.append(list(uniqueValues))  # add the value that correspond to the legend name
            # get indices of unique values
            indVal = []
            for uniqueVal in uniqueValues:
                indVal.append(dfAttr.index[dfAttr[otherCol] == uniqueVal].tolist())
            legendIndices.append(indVal)



    # find common indices for each combination of other columm values
    possibleCombValues = list(itertools.product(*legendValues))
    possibleCombIndices = list(itertools.product(*legendIndices))

    # get the intersection of indices for each legend grouping
    possibleCombIndicesIntersection = []
    legendText = []
    for idx, indComb in enumerate(possibleCombIndices):  # for each combination of values
        possibleCombIndicesIntersection.append(set.intersection(*map(set, indComb)))
        legStr = ''
        for idx0, name in enumerate(legendNames):
            legStr = legStr + name + ': ' + str(possibleCombValues[idx][idx0]) + ' '

        legendText.append(legStr)

    # plot each line
    plt.figure(figsize=(10,8))
    for idx, combIdx in enumerate(possibleCombIndicesIntersection):
        #xIdx = list(combIdx)  # the indicies for x
        #yIdx = [y.index[i] for i in combIdx]
        xPlot = pd.to_numeric(x.loc[combIdx])
        yPlot = pd.to_numeric(y.loc[combIdx])
        idxSort = np.argsort(xPlot).tolist()
        plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort], '-*')

    plt.ylabel(plotRes)
    # TODO: grab x label values from component descriptor, or..?
    plt.xlabel(plotAttr)
    plt.legend(legendText)
    plt.show()
    plt.savefig(plotRes + 'Vs' + plotAttr + '.png')


