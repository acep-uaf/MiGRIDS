# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def fixBadData(df,setupDir,projectName):

    # cd to setup directory, load the projectSetup.xml file and check the time series for bad data.


    # temporary fix

    # df_fixed is the fixed data (replaced bad data with approximated good data)
    df_fixed = df
    # ind of bad data in the original array
    badInd = None
    # stdDiff is the standard deviation of the difference between the fixed and old data for each column
    stdDiff = None
    # oldMean is the mean of each channel in the original df
    import numpy as np
    oldMean = None
    # fixedMean is the new mean for each channel
    fixedMean = None
    #oldMax is the old max for each channel
    oldMax = None
    # fixedMax is the new max for each channel
    fixedMax = None
    oldMin = None
    fixedMin = None


    return df_fixed, badInd


