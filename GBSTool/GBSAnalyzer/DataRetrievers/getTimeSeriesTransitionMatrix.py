# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:51:41 2018

@author: jbvandermeer
"""
# imports
import numpy as np

def getTransitionMatrix(timeSeries,numStates=100):
    '''
    This function generates the transfer function between discrete levels in a time series
    :param timeSeries: input time series
    :param numStates: the number of states to divide time series data into.
    :return: a transition matrix and the bins
    '''

    # seperate into bins
    bins = np.linspace(np.min(timeSeries), np.max(timeSeries)+1, numStates)

    # bin data
    binIdx =  np.digitize(timeSeries,bins)

    # generate transition matrix
    # blank matrix
    TM = np.array([[0]*numStates]*numStates)
    # for each bin number in time series, update transition matrix
    for idx in range(len(binIdx)-1):
        TM[binIdx[idx]][binIdx[idx+1]] += 1

    TM = TM.astype(float) # convert to float to allow to normalize

    # normalize rows
    for row in TM:
        if sum(row) > 0:
            row[:] = row/sum(row)

    # find where sum of a row is 0
    rowSums = np.sum(TM,axis=1)
    nullRows = np.where(rowSums==0)[0]
    # replace with a good row
    for nullRow in nullRows: # for all null rows
        # look for next full row
        nextRows = np.where(rowSums[nullRow:]!=0)[0]
        if len(nextRows)!=0: # if there is a full after the empty row, replace the empty with the first one
            TM[nullRow,:] = TM[(nextRows[0]+nullRow),:]
        else: # if not, replace with the first previous full row
            prevRows = np.where(rowSums[:nullRow]!=0)[0]
            TM[nullRow, :] = TM[prevRows[-1], :]


    return TM, bins