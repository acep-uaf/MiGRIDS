# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 22, 2018
# License: MIT License (see LICENSE file of this package for more information)

import pandas as pd

from Analyzer.DataRetrievers.readNCFile import readNCFile
from Controller.GBSExceptions.TimeStampVectorError import TimeStampVectorError


def getDataChannels(projectPath, dataPath, channelList):
    """
    Retrieves data channels based on list of channels requested. ASSUMES that all channels have a uniform time vector.

    :param projectPath: [string] path to the projects root folder
    :param dataPath: [string] path to the specific data folder
    :param channelList: [List of strings] explicit list of channels to retrieve
    :return dataPackage: [DataFrame] package of channels, first column is time, rest follows 'channelList', index is ints
    """

    # Flag to ensure that only one time channel is loaded.
    timeLoaded = False

    # if channelList is only one item, we need to turn it into a list first
    if isinstance(channelList, str):
        channelList = list([channelList])

    for channelName in channelList:
        filePath = projectPath + dataPath + channelName + '.nc'
        ncHandle = readNCFile(filePath)
        value = (pd.Series(ncHandle.value[:]) + float(ncHandle.offset)) * float(ncHandle.scale)
        time = pd.Series(ncHandle.time[:])

        # Load time stamps once
        if not timeLoaded:
            dataPackage = pd.DataFrame(time.values, time.index, ['time'])
            timeLoaded = True

        # Load the data, if it is the same length as the initial time vector
        if value.shape[0] == dataPackage.shape[0]:
            dataPackage[channelName] = value.values
        else:
            raise TimeStampVectorError(channelName, 'Length of channel does not match time vector.')

    return dataPackage


