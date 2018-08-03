# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 27, 2018
# License: MIT License (see LICENSE file of this package for more information)

import warnings

import numpy as np
import pandas as pd


def getDataSubsets(dataframe, method, otherInputs):
    """
    Interface to extractors for short time-series from the overall dataset using a defined method to allow for quicker
        model runs during searches in the optimization space.
    :param dataframe: [Dataframe] contains full time-series of necessary model input channels
    :param method: [String] used to define the method for extraction. Currently only 'RE-load-one-week' is implemented.
    :param otherInputs: [list(str)] bin for additional parameters for implemented methods.
    :return datasubsets: [Dataframe of dataframes] the subsets of timeseries for all input channels required to run the
        model organized depending on method of extraction.
    :return databins: [DataFrame] provides weights each data frame in datasubsets should be given when extrapolating results.
        This dataframe has two columns of the same length as the original time series. Column 'loadBins' contains the
        binning based on average load (min = 1, mean = 2, max = 3), column 'varGenBins' does the same for the variable
        generation dimension.
    """


    # Method selector

    # If RE-load-one-week is selected, pass the job to getDataSubsetsRELoadOneWeek
    if method == 'RE-load-one-week':
        datasubsets , databins = getDataSubsetsRELoadOneWeek(dataframe, otherInputs)

    # If noReduction is selected just return the input dataframe and an empty databins frame
    # TODO check that this is handled correctly in the fitness calculators, particularly the weightedRawFitness
    # retrieval.
    elif method == 'noReduction':
        datasubsets = dataframe
        databins = pd.DataFrame([])

    else: #if no valid method for data subset retrieval was selected, raise an exception and exit
        raise ValueError('Method specified for data subset calculation is unknown.')

    return datasubsets, databins