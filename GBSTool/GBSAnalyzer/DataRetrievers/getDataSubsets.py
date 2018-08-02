# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 27, 2018
# License: MIT License (see LICENSE file of this package for more information)

import warnings

import numpy as np
import pandas as pd


def getDataSubsets(dataframe, method):
    '''
    Extracts short time-series from the overall dataset using a defined method to allow for quicker model runs during
    searches in the optimization space.
    :param dataframe: [Dataframe] contains full time-series of necessary model input channels
    :param method: [String] used to define the method for extraction. Currently only 'RE-load-one-week' is implemented.
    :return datasubsets: [Dataframe of dataframes] the subsets of timeseries for all input channels required to run the
        model organized depending on method of extraction.
    :return databins: [DataFrame] provides weights each data frame in datasubsets should be given when extrapolating results.
        This dataframe has two columns of the same length as the original time series. Column 'loadBins' contains the
        binning based on average load (min = 1, mean = 2, max = 3), column 'varGenBins' does the same for the variable
        generation dimension.
    '''


    # Method selector
    if method == 'RE-load-one-week':
        # FUTUREFEATURE: the individual methods should be moved into separate files for ease of editing. The getDataSubsets file should just serve as the interface.

        # TODO set correct window size based on actual data time steps and desired data subset length
        # Window size: one week in seconds
        wdwSize = 60*60*24#*7

        # Get rolling one week load averages. We assume that time units are seconds here.
        # just for convenience and readability we'll pull the dataframe apart
        time = pd.Series(dataframe['time'])
        firmLoadP = pd.Series(dataframe['firmLoadP'])
        varGenP = pd.Series(dataframe['varGenP'])

        # Inspect sampling rate to determine number of samples per week
        srates = time.diff()
        srate = srates.mean()
        srateStd = srates.std()
        if srateStd > 0:
            warnings.warn('Non-uniform time vector detected. User is advised that gaps in the time vector can cause unreliable and unwanted behavior.')

        # Inspect length of time vector to determine if there is at least one week of record
        timeLength = time[-1:] - time[0]
        #print(timeLength[timeLength.index.max()])
        if timeLength[timeLength.index.max()] < 60*60*24*7:
            warnings.warn('Input samples are less than one week long. Data reduction with RE-load-one-week method not possible. Full data set will be used.')

        # Run through load channel and find week w least avg load, mean avg load and max avg load
        # AND Run through combined RE channels to find week w least avg RE P, mean avg RE P and max avg RE P
        # If the sampling rate is not one sample per second we need to adjust the window size
        wind = int(np.round(wdwSize/srate))
        firmLoadPWklyAvg = firmLoadP.copy()
        firmLoadPWklyMax = firmLoadP.copy()
        firmLoadPWklyMin = firmLoadP.copy()

        varGenPWklyAvg = varGenP.copy()
        varGenPWklyMax = varGenP.copy()
        varGenPWklyMin = varGenP.copy()

        for indx in range(0, timeLength.index.max(), wind):
            # Load calculations
            firmLoadPWklyAvg[indx:indx+wind] = firmLoadP[indx:indx+wind].mean()
            firmLoadPWklyMax[indx:indx+wind] = firmLoadP[indx:indx+wind].max()
            firmLoadPWklyMin[indx:indx+wind] = firmLoadP[indx:indx + wind].min()

            # Variable RE calculations
            varGenPWklyAvg[indx:indx+wind] = varGenP[indx:indx+wind].mean()
            varGenPWklyMax[indx:indx+wind] = varGenP[indx:indx + wind].max()
            varGenPWklyMin[indx:indx+wind] = varGenP[indx:indx + wind].min()

        # Get the mean load week
        meanDiff = (firmLoadPWklyAvg - firmLoadPWklyAvg.mean()).abs()
        minDiffIdx = meanDiff.idxmin()
        meanLoadTime = time[minDiffIdx:minDiffIdx+wind]
        firmLoadPMean = firmLoadP[minDiffIdx:minDiffIdx+wind]
        varGenPLoadMean = varGenP[minDiffIdx:minDiffIdx+wind]

        # Get the max load week
        maxIdx = firmLoadPWklyMax.idxmax()
        maxLoadTime = time[maxIdx:maxIdx+wind]
        firmLoadPMax = firmLoadP[maxIdx:maxIdx+wind]
        varGenPLoadMax = varGenP[maxIdx:maxIdx+wind]

        # Get the min load week
        minIdx = firmLoadPWklyMax.idxmin()
        minLoadTime = time[minIdx:minIdx + wind]
        firmLoadPMin = firmLoadP[minIdx:minIdx + wind]
        varGenPLoadMin  = varGenP[minIdx:minIdx + wind]

        # Get the mean var gen week
        meanDiffVG = (varGenPWklyAvg - varGenPWklyAvg.mean()).abs()
        minDiffIdxVG = meanDiffVG.idxmin()
        meanVGTime = time[minDiffIdxVG:minDiffIdxVG+wind]
        firmLoadPVGMean = firmLoadP[minDiffIdxVG:minDiffIdxVG+wind]
        varGenPMean = varGenP[minDiffIdxVG:minDiffIdxVG+wind]

        # Get the max var gen week
        maxIdxVG = varGenPWklyMax.idxmax()
        maxVGTime = time[maxIdxVG:maxIdxVG+wind]
        firmLoadPVGMax = firmLoadP[maxIdxVG:maxIdxVG+wind]
        varGenPMax = varGenP[maxIdxVG:maxIdxVG+wind]

        # Get the min var gen week
        minIdxVG = varGenPWklyMin.idxmin()
        minVGTime = time[minIdxVG:minIdxVG + wind]
        firmLoadPVGMin = firmLoadP[minIdxVG:minIdxVG + wind]
        varGenPMin = varGenP[minIdxVG:minIdxVG + wind]
        
        # Create data binning
        # We will bin by similarity. That is, we check if the weekly mean is closest to min/mean/max and bin accordingly

        # Set up binning dimensions first:
        firmLoadPBin = firmLoadP.copy()
        varGenPBin = varGenP.copy()

        for indx in range(0, timeLength.index.max(), wind):
            # Load binning
            minDiff = (firmLoadP[indx:indx+wind] - firmLoadPMin.mean()).abs()
            minDiff = minDiff.mean()
            meanDiff = (firmLoadP[indx:indx+wind] - firmLoadPMean.mean()).abs()
            meanDiff = meanDiff.mean()
            maxDiff = (firmLoadP[indx:indx+wind] - firmLoadPMax.mean()).abs()
            maxDiff = maxDiff.mean()
            if (minDiff < meanDiff) & (minDiff < maxDiff):
                firmLoadPBin[indx:indx+wind] = 1
            elif (meanDiff <= minDiff) & (meanDiff <= maxDiff):
                firmLoadPBin[indx:indx+wind] = 2
            else:
                firmLoadPBin[indx:indx+wind] = 3
            
            #Var Gen binning
            minDiff = (varGenP[indx:indx + wind] - varGenPMin.mean()).abs()
            minDiff = minDiff.mean()
            meanDiff = (varGenP[indx:indx + wind] - varGenPMean.mean()).abs()
            meanDiff = meanDiff.mean()
            maxDiff = (varGenP[indx:indx + wind] - varGenPMax.mean()).abs()
            maxDiff = maxDiff.mean()
            if (minDiff < meanDiff) & (minDiff < maxDiff):
                varGenPBin[indx:indx + wind] = 1
            elif (meanDiff <= minDiff) & (meanDiff <= maxDiff):
                varGenPBin[indx:indx + wind] = 2
            else:
                varGenPBin[indx:indx + wind] = 3

        # assemble data sets
        datasubsetMinLoad = pd.DataFrame({'time': minLoadTime, 'firmLoadP': firmLoadPMin, 'varGenP': varGenPLoadMin})
        datasubsetMeanLoad = \
            pd.DataFrame({'time': meanLoadTime, 'firmLoadP': firmLoadPMean, 'varGenP': varGenPLoadMean})
        datasubsetMaxLoad = pd.DataFrame({'time': maxLoadTime, 'firmLoadP': firmLoadPMax, 'varGenP': varGenPLoadMax})
        datasubsetMinVG = pd.DataFrame({'time': minVGTime, 'firmLoadP': firmLoadPVGMin, 'varGenP': varGenPMin})
        datsubsetMeanVG = pd.DataFrame({'time': meanVGTime, 'firmLoadP': firmLoadPVGMean, 'varGenP': varGenPMean})
        datasubsetMaxVG = pd.DataFrame({'time': maxVGTime, 'firmLoadP': firmLoadPVGMax, 'varGenP': varGenPMax})

        # assemble output DF
        datasubsetsTemp = {'MinLoad': datasubsetMinLoad, 'MeanLoad': datasubsetMeanLoad, 'MaxLoad': datasubsetMaxLoad,
                           'MinVarGen': datasubsetMinVG, 'MeanVarGen': datsubsetMeanVG, 'MaxVarGen': datasubsetMaxVG}
        datasubsets = pd.concat(datasubsetsTemp, keys=['MinLoad', 'MeanLoad', 'MaxLoad',
                                                       'MinVarGen', 'MeanVarGen', 'MaxVarGen'])

        # Snippet to retrieve datasubset toplevel multiIndex names.
        #names = list(set(datasubsets.index.get_level_values(0))))

        # assemble databins variable
        databins = pd.DataFrame({'loadBins': firmLoadPBin, 'varGenBins': varGenPBin})

    else: #if no valid method for data subset retrieval was selected, raise an exception and exit
        raise ValueError('Method specified for data subset calculation is unknown.')

    return datasubsets, databins