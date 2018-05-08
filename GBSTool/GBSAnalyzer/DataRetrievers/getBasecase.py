# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: March 29, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Helper to get information about the base case (from input data).

import os
from distutils.util import strtobool

import pandas as pd
from bs4 import BeautifulSoup as soup

from GBSAnalyzer.DataRetrievers.getDataChannels import getDataChannels
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile


def getBasecase(projectName, rootProjectPath):
    '''
    Retrieve base case data and meta data required for initial estimate of search space boundaries and data
    sparsing.
    FUTUREFEATURE: Note that this does its own load calculation, which may be redundant or differ from load calculations
        done in the GBSInputHandler. This should be revisited in the future.
    :return time: [Series] time vector
    :return firmLoadP: [Series] firm load vector
    :return varLoadP: [Series] variable (switchable, manageable, dispatchable) load vector
    :return firmGenP: [Series] firm generation vector
    :return varGenP: [Series] variable generation vector
    :return allGenP: [DataFrame] contains time channel and all generator channels.
    '''

    # Read project meta data to get (a) all loads, (b) all generation, and their firm and variable subsets.
    setupMetaHandle = open(os.path.join(rootProjectPath, 'InputData/Setup/' + projectName + 'Setup.xml'), 'r')
    setupMetaData = setupMetaHandle.read()
    setupMetaHandle.close()
    setupMetaSoup = soup(setupMetaData, 'xml')

    # Retrieve the time and firm load vectors
    firmLoadPFileName = setupMetaSoup.loadProfileFile.get('value')
    firmLoadPFile = readNCFile \
        (os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/' + firmLoadPFileName))
    time = pd.Series(firmLoadPFile.time[:])

    firmLoadP = pd.Series((firmLoadPFile.value[:] + firmLoadPFile.offset ) * firmLoadPFile.scale)

    # Setup other data channels
    firmGenP = pd.Series(firmLoadP.copy() * 0)
    varGenP = pd.Series(firmLoadP.copy() * 0)
    varLoadP = pd.Series(firmLoadP.copy() * 0)
    allGenP = pd.DataFrame(time, columns=['time'])

    # Get list if all components
    components = setupMetaSoup.componentNames.get('value').split()
    # Step through the given list of components and assign them to the correct data channel if appropriate
    for cpt in components:
        # load meta data for the component
        cptMetaHandle = open(os.path.join(rootProjectPath, 'InputData/Components/' + cpt +'Descriptor.xml'), 'r')
        cptMetaData = cptMetaHandle.read()
        cptMetaHandle.close()
        cptMetaSoup = soup(cptMetaData, 'xml')

        # Read the type, if it is a source it is going into one of the generation channels
        if cptMetaSoup.type.get('value') == 'source':
            # Check if it can load follow, if true add it to the firmGenP channel
            if strtobool(cptMetaSoup.isLoadFollowing.get('value')):
                # Load associated time series - actual power for firmGenP
                chName = cptMetaSoup.component.get('name') + 'P'
                tempDf = getDataChannels(rootProjectPath, '/InputData/TimeSeriesData/ProcessedData/', chName)
                val = pd.Series(tempDf[chName])
                firmGenP = firmGenP + val

                # Also add it to the allGenP dataframe
                dfVal = pd.DataFrame(val, columns=[chName])
                allGenP = pd.concat([allGenP, dfVal], axis=1)

            # If it cannot load follow, it is a variable generator
            else:  # not strtobool(cptMetaSoup.isLoadFollowing.get('value'))
                # Load associated time series - PAvail for varGenP if it exists
                chName = cptMetaSoup.component.get('name') + 'PAvail'
                if os.path.isfile(
                        os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/', chName + '.nc')):
                    tempDf = getDataChannels(rootProjectPath, '/InputData/TimeSeriesData/ProcessedData/', chName)
                else:
                    chName = cptMetaSoup.component.get('name') + 'P'
                    tempDf = getDataChannels(rootProjectPath, '/InputData/TimeSeriesData/ProcessedData/', chName)
                val = pd.Series(tempDf[chName])
                varGenP = varGenP + val

        # if the type is source, and the name is not the same as the one in firmLoadPFileName, add to varLoadP
        elif cptMetaSoup.type.get('value') == 'sink' and cptMetaSoup.component.get('name') != firmLoadPFileName[:-3]:
            # Load associated time series - PAvail for varLoadP if it exists
            chName = cptMetaSoup.component.get('name') + 'PAvail'
            if os.path.isfile(os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/', chName + '.nc')):
                tempDf = getDataChannels(rootProjectPath, '/InputData/TimeSeriesData/ProcessedData/', chName)
            else:
                chName = cptMetaSoup.component.get('name') + 'P'
                tempDf = getDataChannels(rootProjectPath, '/InputData/TimeSeriesData/ProcessedData/', chName)
            val = pd.Series(tempDf[chName])
            # add to the varLoadP variable
            varLoadP = varLoadP + val

        # if the type is sink-source (or source-sink, to plan for silly users...) add to varLoadP if negative and
        # firmGenP is positive. This follows the sign convention discussed for energy storage (positive TOWARDS the
        # grid; negative FROM the grid), see issue #87. And it posits that energy storage is either a variable load
        # or firm generation (with variable PAvail).
        elif cptMetaSoup.type.get('value') == 'sink-source' or cptMetaSoup.type.get('value') == 'source-sink':
            # Load associated time series - actual power for firmGenP
            chName = cptMetaSoup.component.get('name') + 'P'
            tempDf = getDataChannels(rootProjectPath, '/InputData/TimeSeriesData/ProcessedData/', chName)
            val = pd.Series(tempDf[chName])
            # Add positive data points to firmGenP
            positiveData = val.copy()
            positiveData[positiveData < 0] = 0
            firmGenP = firmGenP + positiveData
            # Add negative data points to varLoadP
            negativeData = val.copy()
            negativeData[negativeData > 0] = 0
            negativeData = -1 * negativeData  # since we're now adding this to a load, we need to flip the sign
            varLoadP = varLoadP + negativeData

        # if it wasn't sink, source, or sink-source, the component type is `grid` or not defined. In the later case
        # we'll issue a warning.
        else:
            if cptMetaSoup.type.get('value') != 'grid':
                raise UserWarning('Type for %s is not (properly) defined.', cptMetaSoup.component.get('name'))


    # Return the calculated channels
    return time, firmLoadP, varLoadP, firmGenP, varGenP, allGenP