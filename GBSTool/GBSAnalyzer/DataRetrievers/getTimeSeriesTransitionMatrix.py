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
    bins = np.linspace(min(timeSeries[0]), max(timeSeries[0])+1, numStates)

    # bin data
    binIdx =  np.digitize(timeSeries[0],bins)

    # generate transition matrix
    # blank matrix
    TM = np.array([[0]*numStates]*numStates)
    # for each bin number in time series, update transition matrix
    for idx in range(len(binIdx)-1):
        TM[binIdx[idx]][binIdx[idx+1]] += 1

    TM.dtype = float # convert to float to allow to normalize

    # normalize rows
    for row in TM:
        if sum(row) > 0:
            row[:] = row/sum(row)

    return TM, bins