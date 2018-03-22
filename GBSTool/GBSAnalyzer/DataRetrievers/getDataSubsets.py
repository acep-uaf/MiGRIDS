# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 27, 2018
# License: MIT License (see LICENSE file of this package for more information)

def getDataSubsets(dataframe, method):
    '''
    Extracts short time-series from the overall dataset using a defined method to allow for quicker model runs during
    searches in the optimization space.
    :param dataframe: [Dataframe] contains full time-series of all model input channels
    :param method: [String] used to define the method for extraction. Currently only 'RE-load-one-week' is implemented.
    :return datasubsets: [Dataframe of dataframes] the subsets of timeseries for all input channels required to run the
        model organized depending on method of extraction.
    :return databins: [Series] provides weights each data frame in datasubsets should be given when extrapolating results.
    '''

    # Empty bins
    datasubsets = []
    databins = []

    # TODO: implement
    if method == 'RE-load-one-week':
        # Get rolling one week load averages. We assume that time units are seconds here.
        time = dataframe['time']


    else: #if no valid method for data subset retrieval was selected, raise an exception and exit
        raise ValueError('Method specified for data subset calculation is unknown.')

    return datasubsets, databins