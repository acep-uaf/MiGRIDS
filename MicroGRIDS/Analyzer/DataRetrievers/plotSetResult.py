#imports
import numpy as np
import os
import sqlite3
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import numbers

def plotSetResult(plotRes,plotAttr, projectSetDir = '', otherAttr = [],otherAttrVal = [], removeOtherAttr = [], baseSet = '', baseRun = '',
                  subtractFromBase = 0, removeSingleOtherAttr = True, alwaysUseMarkers = False, plotResName = '',
                  plotAttrName = '', otherAttrNames = [], saveName = ''):
    '''
    plot a single result for a set of simulations
    :param plotRes: the database column header of the variable to plot, or a dict identifying column headers and number with variable names and an equation to evaluate them.
    In the equation, the variable names must be surrounded by '#'.
    For example: {'EESS Equivalent Cycles':{'Energy Storage Discharge kWh':'x', 'ees0.PInMaxPa.value':'y', 'ees0.ratedDuration.value':'z',
                                          'eqn':'#x#/(#y#*#z#/3600)'}}
    It can also be a dict in the form: {'Generator Import [GWh]':{'Generator Import kWh':'+',1000000:'/'}), where instead
    of identifying a variable for each column and nuber,an operand is identified. They will be solved in the order they
    are listed. This is for simpler calculations.
    :param plotAttr: The simulation attribute to be plotted against. This is the column header in the database as well as the tag and attribute from the component or setup xml file.
    :param otherAttr: The other component or setup attributes to have fixed values in the plot. If not specified, all values for the attribute will be plotted as multiple lines.
    :param otherAttrVal: The values of the 'otherAttr' to plot. It should be given as a list of lists, corresponding to otherAttr.
    :param removeOtherAttr: a list of other attributes to remove from the legend. These are for attributes that only have one
    value for every other combination of values.
    :param baseSet: the set identifier of the base set. If left as '', then no base case is plotted.
    :param baseRun: the run number of the base set. If left as '', then no base case is plotted.
    :param subtractFromBase:0  - do not subtract or add, but if base case is specified, place at the begining
# 1 - subtract value from base -> decrease from base case
# 2 - subtract base from value -> increase from base case
    :param plotAttrName: the desired x axis label
    :param otherAttrNames: a dict of the other attribute variable names that will go in the legend and the names desired to be used in the legend
    :param saveName: the name to save the plots as. If left '', then a default naming convetion will be used.
    :return: Nothing
    '''
    if projectSetDir == '':
        print('Choose the directory for the set of simulations')
        root = tk.Tk()
        root.withdraw()
        projectSetDir = filedialog.askdirectory()

    # get the set number
    dirName = os.path.basename(projectSetDir)
    setNum = dirName[3:]
    #try:
    #    setNum = int(dirName[3:])
    #except ValueError:
    #    print(
    #       'The directory name for the simulation set results does not have the correct format. It needs to be \'Setx\' where x is the run number.')

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

            # get the base value
            yBase = pd.to_numeric(getPlotRes(plotRes, dfBase).loc[baseRun])
            xBase = pd.to_numeric(getPlotRes(plotAttr, dfBase).loc[baseRun])

    else: # if no base case set
        yBase = 0
        xBase = 0


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

    # remove values from otherAttr not to be plotted, only if values to be plotted have been specified
    if otherAttrVal != []:
        otherAttrValUse = otherAttrVal
        includeAttrValInFileName = True # include attribute values in the saved figure name
        for idx, attr in enumerate(otherAttr):  # for set of values to plot for this attribute
            values = otherAttrVal[idx]
            # convert to numeric, if not already
            values = [float(x) for x in values]
            # go through each value for this attribute, check if it is in the list of values to plot, if not, remove row
            # from both dfAttr and dfRes
            dropIdx = []  # df indicies to drop
            for idx0, attrVal in enumerate(dfAttr[attr]):
                if not float(attrVal) in values:
                    # get the index of the row to be dropped and remove from both df
                    dropIdx.append(dfAttr.index[idx0])
                    # dfAttr = dfAttr.drop(dfIdx)
                    # dfRes = dfRes.drop(dfIdx)
            dfAttr = dfAttr.drop(dropIdx)
            dfRes = dfRes.drop(dropIdx)
    else:
        includeAttrValInFileName = False  # include attribute values in the saved figure name
        otherAttrValUse = []
        for idx, attr in enumerate(otherAttr):
            try: # try to convert to intergers
                # make unique with set
                otherAttrValUse.append(list(set([int(x) for x in dfAttr[attr]])))
            except:
                otherAttrValUse.append(list(set([float(x) for x in dfAttr[attr]])))

    # get the names of all results columns
    columns = list(dfAttr.columns.values)

    x = dfAttr[plotAttr]
    y = getPlotRes(plotRes, dfRes)

    # group according to other columns
    otherColumns = columns.copy()
    otherColumns.remove(plotAttr)
    # check if input and output ess power are listed
    for roa in removeOtherAttr:
        try:
            otherColumns.remove(roa)
        except:
            ValueError('RemoveOtherAttr value was not found in the component attributes that were changed for this set of simulations.')
    if 'ees0.POutMaxPa.value' in otherColumns and 'ees0.PInMaxPa.value' in otherColumns:
        # if they are, and they are identical, remove one.
        if all(dfAttr['ees0.POutMaxPa.value'] == dfAttr['ees0.PInMaxPa.value']):
            otherColumns.remove('ees0.PInMaxPa.value')
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
        if any(dfAttr[otherCol] != dfAttr[plotAttr]) and otherCol.lower() != 'started' and otherCol.lower() != 'finished':  # make sure not identical (this is an option when setting values of 2 different attributes

            uniqueValues = np.unique(dfAttr[otherCol])  # unique values of this column
            # do not add other legend entries if they only have one value and the setting says so.
            if not(removeSingleOtherAttr and len(uniqueValues) == 1):
                if otherCol in otherAttrNames.keys():
                    legendNames.append(otherAttrNames[otherCol])
                else:
                    legendNames.append(otherCol)  # add col name to legend names
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
                if alwaysUseMarkers:
                    # get marker indices that wrap around when they reach the end of the list of markers
                    indMarker0 = []
                    for idxM in range(len(uniqueValues)):
                        indMarker0.append(indMarker + (idxM % (len(markers)-indMarker)))
                    legendMarkers.append(markers[indMarker0])
                    indMarker = indMarker + 1 % (len(markers)-indMarker)
                    # get line indices that wrap around when they reach the end of the list of lineStyles
                    indLineStyle0 = []
                    for idxL in range(len(uniqueValues)):
                        indLineStyle0.append((indLineStyle + idxL) % len(lineStyles))
                    legendLineStyles.append(lineStyles[indLineStyle0])
                    indLineStyle = indLineStyle + 1 % len(lineStyles)
                else:
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
        yPlot = pd.to_numeric(y.loc[combIdx])

        # check if need to subtract from base value, or not, or add to begging of series. Only if a base case is set.
        if subtractFromBase == 1 and baseSet != '' and baseRun != '':
            yPlot = yBase - yPlot
        elif subtractFromBase == 2 and baseSet != '' and baseRun != '':
            yPlot = yPlot - yBase
        elif subtractFromBase == 0 and baseSet != '' and baseRun != '':
            xPlot = xPlot.append(pd.Series(pd.to_numeric(xBase)), ignore_index=True)
            yPlot = yPlot.append(pd.Series(pd.to_numeric(yBase)), ignore_index=True)


        idxSort = np.argsort(xPlot).tolist()
        # marker and linestyles
        marker = possibleCombMarkers[idx][0]
        lineStyle = possibleCombLineStyles[idx][0]
        if marker == '':
            if lineStyle == '':
                plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort])
            else:
                plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort], linestyle=lineStyle)
        else:
            if lineStyle == '':
                plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort], marker=marker)
            else:
                plt.plot(xPlot.iloc[idxSort], yPlot.iloc[idxSort], marker = marker, linestyle=lineStyle)


    if baseSet != '' and baseRun != '': # if base case was used
        if subtractFromBase == 1:
            plt.ylabel('Reduction in ' + plotResName)
        elif subtractFromBase == 2:
            plt.ylabel('Increase in ' + plotResName)
        elif subtractFromBase == 0:
            plt.ylabel(plotResName)
    else:
        plt.ylabel(plotResName)
    # TODO: grab x label values from component descriptor, or..?
    if plotAttrName != '':
        plt.xlabel(plotAttrName)
    else:
        plt.xlabel(plotAttr)
    plt.legend(legendText)
    #plt.show()
    otherAttrText = ''
    for idx, attr in enumerate(otherAttr):
        # convert values to a string
        oavText = ''
        for idx0, oav in enumerate(otherAttrValUse[idx]):
            if idx0 != 0:
                oavText = oavText + '_'
            oavText = oavText + str(oav).replace('.','_') # replace periods with underscores.
        otherAttrText = otherAttrText + attr + '_' + oavText + ' '

    os.chdir(projectSetDir)
    if not os.path.exists('figs'):
        os.makedirs('figs')
    os.chdir('figs')
    if saveName == '':
        savePlotResName = plotResName.replace('/','_') # replace / char which may be used in the label but not save name
        # only indicate the values plotted in the name if not plotting all values
        if includeAttrValInFileName:
            nameBase = savePlotResName + ' vs ' + plotAttr + ' for ' + otherAttrText
        else:
            nameBase = savePlotResName + ' vs ' + plotAttr
        if baseSet != '' and baseRun != '': # if base case was used, different file name
            if subtractFromBase == 1:
                plt.savefig('Reduction in ' + nameBase + '.png')
                plt.savefig('Reduction in ' + nameBase + '.pdf')
            elif subtractFromBase == 2:
                plt.savefig('Increase in ' + nameBase + '.png')
                plt.savefig('Increase in ' + nameBase + '.pdf')
            elif subtractFromBase == 0:
                plt.savefig(nameBase + '.png')
                plt.savefig(nameBase + '.pdf')
        else:
            plt.savefig(nameBase + '.png')
            plt.savefig(nameBase + '.pdf')
    else:
        plt.savefig(saveName)
    plt.close()

# return the results to be plotted. If it is a list, add together. Otherwise, simply return the result.
def getPlotRes(plotRes,df):
    if isinstance(plotRes, dict):
        if 'eqn' in plotRes.keys():
            '''
            # put spaces around each character in equation string to single out variables
            eqn = ' '
            for char in plotRes['eqn']:
                if char.isdigit() or char=='.': # do not split up numbers
                    eqn = eqn + char
                else:
                    eqn = eqn + char
                    #eqn  = eqn + ' ' + char + ' '
            '''
            eqn = plotRes['eqn']
            for pR, op in plotRes.items():
                if pR != 'eqn':
                    if isinstance(op, (float, int)):
                        eqn = eqn.replace('#' + pR + '#', str(op))
                    else:
                        eqn = eqn.replace( '#' + pR + '#' , 'df[\'' + op + '\'].astype(float)')
                        #eqn = eqn.replace(' ' + op + ' ', 'df[\''+pR+'\'].astype(float)')
            try:
                y = eval(eqn)
            except:
                y = pd.DataFrame([np.nan]*df.shape[0])


        else:
            y = 0
            for pR,op in plotRes.items():
                if op == '+':
                    if isinstance(pR,(float,int)):
                        y = y + pR
                    else:
                        y = y + df[pR].astype('float')
                elif op == '-':
                    if isinstance(pR,(float,int)):
                        y = y - pR
                    else:
                        y = y - df[pR].astype('float')
                elif op == '*':
                    if isinstance(pR,(float,int)):
                        y = y * pR
                    else:
                        y = y * df[pR].astype('float')
                elif op == '/':
                    if isinstance(pR,(float,int)):
                        y = y / pR
                    else:
                        y = y / df[pR].astype('float')
    else:
        y = df[plotRes]

    return y