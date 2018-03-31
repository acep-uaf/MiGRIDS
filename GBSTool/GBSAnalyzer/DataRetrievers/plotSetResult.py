#imports
import numpy as np
import os
import sqlite3
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import itertools
import matplotlib.pyplot as plt

def plotSetResult(plotRes,plotAttr, projectSetDir = '', otherAttr = [],otherAttrVal = [], baseSet = '', baseRun = '', subtractFromBase = True):
    '''
    plot a single result for a set of simulations
    :param plotRes: the database column header of the variable to plot.
    :param plotAttr: The simulation attribute to be plotted against. This is the column header in the database as well as the tag and attribute from the component or setup xml file.
    :param otherAttr: The other component or setup attributes to have fixed values in the plot. If not specified, all values for the attribute will be plotted as multiple lines.
    :param otherAttrVal: The values of the 'otherAttr' to plot. It should be given as a list of lists, corresponding to otherAttr.
    :param baseCaseRunDir: the run directory of the base case scenario.
    :param subtractFromBase: This is True if results are to be subtracted from the basecase. False for the reverse.
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

    # get the base case value, if set
    if baseSet != '' and baseRun != '':
        baseDir = os.path.join(projectSetDir,'..', 'Set'+str(baseSet))
        try:
            os.chdir(baseDir) # go to directory
        except:
            print('The base case set and run could not be found for this project')
        else:
            conn = sqlite3.connect('set' + str(baseSet) + 'Results.db')
            # check if Results table exists, tableName will be empty if not
            tableName = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name='Results';", conn)
            # if not initialized
            if tableName.empty:
                print('No results have been calculated for the base case set yet.')
                return  # exit function
            else:
                dfBase = pd.read_sql_query('select * from Results', conn)

            conn.close()
            yBase = dfBase[plotRes].loc[baseRun]
    else: # if no base case set
        yBase = 0


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
        values = otherAttrVal[idx]
        # convert to numeric, if not already
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
    # for plotting. use numpy array to allow indexing with a list of intergers
    markers = np.array(['*','o','v','^','<','>','x','.','8','s','D','d'])
    lineStyles = np.array([':','-.','--','-'])
    colors = np.array(['b','g','r','c','m','y','k'])
    indMarker = 0 # keeps track of which markers have been assigned to a value already
    indLineStyle = 0
    legendMarkers = []
    legendLineStyles = []
    for idx, otherCol in enumerate(otherColumns):
        if any(dfAttr[otherCol] != dfAttr[plotAttr]) and otherCol.lower() != 'started':  # make sure not identical (this is an option when setting values of 2 different attributes
            legendNames.append(otherCol)  # add col name to legend names
            uniqueValues = np.unique(dfAttr[otherCol])  # unique values of this column
            # check if it can be converted to a float
            try:
                # convert to float and sort uniqueValues
                uniqueValues = np.sort([float(x) for x in uniqueValues])
            except ValueError:
                # do nothing
                uniqueValues = uniqueValues
            legendValues.append(list(uniqueValues))  # add the value that correspond to the legend name
            # linestyles
            # get indices of unique values
            indVal = []
            # check if uniqueValues are float. If so, convert attribute values to float to compare
            if isinstance(uniqueValues[0],float):
                attrVal = [float(x) for x in dfAttr[otherCol]]
            else:
                attrVal = dfAttr[otherCol]

            for uniqueVal in uniqueValues:
                indVal.append(dfAttr.index[attrVal == uniqueVal].tolist())
            legendIndices.append(indVal)
            # append linestyles and marker styles
            if idx%2 != 0: # odd numbers, markers
                # get marker indices that wrap around when they reach the end of the list of markers
                indMarker0 = []
                for idxM in range(len(uniqueValues)):
                    indMarker0.append(indMarker + (idxM % len(markers)))
                legendMarkers.append(markers[indMarker0])
                indMarker = indMarker + 1 % len(markers)
                # append empty list for line styles, indicates does not control which kind of style
                legendLineStyles.append(['']*len(uniqueValues))
            else: # even numbers, line styles
                # get line indices that wrap around when they reach the end of the list of lineStyles
                indLineStyle0 = []
                for idxL in range(len(uniqueValues)):
                    indLineStyle0.append(indLineStyle + (idxL % len(lineStyles)))
                legendLineStyles.append(lineStyles[indLineStyle0])
                indLineStyle = indLineStyle + 1 % len(lineStyles)
                # append empty list for markers, indicates does not control which kind of marker
                legendMarkers.append(['']*len(uniqueValues))

    # find common indices for each combination of other columm values
    possibleCombValues = list(itertools.product(*legendValues))
    possibleCombIndices = list(itertools.product(*legendIndices))
    possibleCombMarkers = list(itertools.product(*legendMarkers))
    possibleCombLineStyles = list(itertools.product(*legendLineStyles))

    # get the intersection of indices for each legend grouping
    possibleCombIndicesIntersection = []
    legendText = []
    for idx, indComb in enumerate(possibleCombIndices):  # for each combination of values
        possibleCombIndicesIntersection.append(set.intersection(*map(set, indComb)))
        legStr = ''
        for idx0, name in enumerate(legendNames):
            if idx0 != 0: # add a coma in between legend entries
                legStr = legStr + ', '

            legStr = legStr + name + ': ' + str(possibleCombValues[idx][idx0])

        legendText.append(legStr)

    # plot each line
    plt.figure(figsize=(10,8))
    for idx, combIdx in enumerate(possibleCombIndicesIntersection):
        #xIdx = list(combIdx)  # the indicies for x
        #yIdx = [y.index[i] for i in combIdx]
        xPlot = pd.to_numeric(x.loc[combIdx])

        # check if need to subtract from base value, or not.
        if subtractFromBase:
            yPlot = yBase - pd.to_numeric(y.loc[combIdx])
        else:
            yPlot = pd.to_numeric(y.loc[combIdx]) - yBase

        idxSort = np.argsort(xPlot).tolist()
        # marker and linestyles
        marker = possibleCombMarkers[idx][0]
        lineStyle = possibleCombLineStyles[idx][1]
        plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort], marker = marker, linestyle = lineStyle )

    if baseSet != '' and baseRun != '': # if base case was used
        if subtractFromBase:
            plt.ylabel('Reduction in ' + plotRes)
        else:
            plt.ylabel('Increase in ' + plotRes)
    else:
        plt.ylabel(plotRes)
    # TODO: grab x label values from component descriptor, or..?
    plt.xlabel(plotAttr)
    plt.legend(legendText)
    #plt.show()
    otherAttrText = ''
    for idx, attr in enumerate(otherAttr):
        # convert values to a string
        oavText = ''
        for idx, oav in enumerate(otherAttrVal[idx]):
            if idx != 0:
                oavText = oavText + '_'
            oavText = oavText + str(oav)
        otherAttrText = otherAttrText + attr + '_' + oavText + ' '


    if baseSet != '' and baseRun != '': # if base case was used, different file name
        if subtractFromBase:
            plt.savefig('Reduction in ' + plotRes + ' vs ' + plotAttr + ' for ' + otherAttrText + '.png')
        else:
            plt.savefig('Increase in ' + plotRes + ' vs ' + plotAttr + ' for ' + otherAttrText + '.png')
    else:
        plt.savefig(plotRes + ' vs ' + plotAttr + ' for ' + otherAttrText + '.png')

