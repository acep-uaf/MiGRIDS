# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 22, 2018
# License: MIT License (see LICENSE file of this package for more information)

import netCDF4
import pandas as pd
from GBSController.GBSExceptions.TimeStampVectorError import TimeStampVectorError

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

    for channelName in channelList:
        filePath = projectPath + dataPath + channelName + '.nc'

        value, time = loadData(filePath)

        # Load time stamps once
        if not timeLoaded:
            dataPackage = pd.DataFrame(time.values, time.index)
            timeLoaded = True

        # Load the data, if it is the same length as the initial time vector
        if value.shape[0] == dataPackage.shape[0]:
            dataPackage[channelName] = value.values
        else:
            raise TimeStampVectorError(channelName, 'Length of channel does not match time vector.')

    return dataPackage


def loadData(filePath):
    """
    Helper function to load a netCDF data file.
    :param filePath:
    :return value: [Series] the series of values from the netCDF file
    :return time: [Series] the series of time stamps in UNIX epoch from the netCDF file
    """
    nc = netCDF4.Dataset(filePath)
    value = pd.Series(nc.variables['value'][:])
    time = pd.Series(nc.variables['time'][:])

    nc.close()

    return value, time
