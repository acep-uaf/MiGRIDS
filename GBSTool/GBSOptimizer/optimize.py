#Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains the main flow of the optimization as it is to be called from the GBSController.

import os
from distutils.util import strtobool

import pandas as pd
from bs4 import BeautifulSoup as soup

from GBSAnalyzer.DataRetrievers.getDataChannels import getDataChannels
from GBSAnalyzer.DataRetrievers.getDataSubsets import getDataSubsets
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile


class optimize:
    '''
    TODO: document this
    '''

    def __init__(self, projectName, searchArgs):
        '''
        Constructor
        TODO: implement

        :param projectName: [String] name of the project, used to locate project folder tree within the GBSProject
            folder structure
        :param searchArgs: [Array of strings] parameters defining the search objectives and methods to be used.
            searchArgs[0]: searchMethod used to determine which search algorithm to dispatch. Currently implemented is
            'simulatedAnnealing'.
            searchArgs[1]: optimizationObjective TODO define this. It should allow blending of objectives.
            searchArgs[2]: dataReductionMethod: the method used to find shorter characteristic input time-series,
                currently only 'RE-load-one-week' is supported as input.
            searchArgs[3]: boundaryMethod: defines the method with which the optimization boundaries are determined.
                Currently, only 'variableSRC' is supported.
        '''

        # Setup key parameters
        self.thisPath = os.path.dirname(os.path.realpath(__file__))
        self.projectName = projectName
        self.rootProjectPath = self.thisPath + '/../../GBSProjects/' + self.projectName # root path to project files relative to this file location
        self.searchMethod = searchArgs[0]
        self.optimizationObjective = searchArgs[1]
        self.dataReductionMethod = searchArgs[2]  # should be 'RE-load-one-week'
        self.boundaryMethod = searchArgs[3]     # should be 'variableSRC'

        # Retrieve data from base case (Input files)
        self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP = \
            self.getBasecase(self.projectName, self.rootProjectPath)

        # Calculate boundaries for optimization search
        self.minESSPPa, self.maxESSPPa, self.minESSEPa, self.maxESSEPa = \
            self.getOptimizationBoundaries(self.boundaryMethod, self.time, self.firmLoadP, self.varLoadP,
                                           self.firmGenP, self.varGenP, otherConstraints=None)

        # Get the short test time-series
        # TODO assemble input dataframe
        reductionInput = pd.DataFrame([self.time, self.firmLoadP, self.varGenP], self.time, ['time', 'firmLoadP', 'varGenP'])
        self.abbrevDatasets, self.abbrevDatasetWeights = getDataSubsets(df, self.dataReductionMethod)

        # Setup optimization runs
        # Branch based on input from 'searchArgs'
        # NOTE: we need to get the KPI for the base case somewhere here to compare results against
        if self.searchMethod == 'simulatedAnnealing':
            # call simualtedAnnealing functions
            a = 0
        # FUTUREFEATURE: add further optimization methods here
        else:
            raise ValueError('Unknown optimization method, %s, selected.' % searchArgs[0])






    def getBasecase(self, projectName, rootProjectPath):
        '''
        Retrieve base case data and meta data required for initial estimate.
        :return time: [Series] time vector
        :return firmLoadP: [Series] firm load vector
        :return varLoadP: [Series] variable (switchable, manageable, dispatchable) load vector
        :return firmGenP: [Series] firm generation vector
        :return varGenP: [Series] variable generation vector
        '''

        print(rootProjectPath)

        # Read project meta data to get (a) all loads, (b) all generation, and their firm and variable subsets.
        setupMetaHandle = open(os.path.join(rootProjectPath, 'InputData/Setup/' + projectName + 'Setup.xml'), 'r')
        setupMetaData = setupMetaHandle.read()
        setupMetaHandle.close()
        setupMetaSoup = soup(setupMetaData, 'xml')

        # Retrieve the time and firm load vectors
        firmLoadPFileName = setupMetaSoup.loadProfileFile.get('value')
        firmLoadPFile = readNCFile(os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/' + firmLoadPFileName))
        time = pd.Series(firmLoadPFile.time)
        firmLoadP = pd.Series((firmLoadPFile.value[:] + firmLoadPFile.offset)* firmLoadPFile.scale)

        # Setup other data channels
        firmGenP = pd.Series(firmLoadP.copy()*0)
        varGenP = pd.Series(firmLoadP.copy()*0)
        varLoadP = pd.Series(firmLoadP.copy() * 0)

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
                # If it cannot load follow, it is a variable generator
                else: # not strtobool(cptMetaSoup.isLoadFollowing.get('value'))
                    # Load associated time series - PAvail for varGenP if it exists
                    chName = cptMetaSoup.component.get('name') + 'PAvail'
                    print(chName + ': ' + os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/', chName + '.nc') + ' : '+ str(os.path.isfile(os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/', chName + '.nc'))))
                    if os.path.isfile(os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/', chName + '.nc')):
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
            elif cptMetaSoup.type.get('value') =='sink-source' or cptMetaSoup.type.get('value') == 'source-sink':
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
        return time, firmLoadP, varLoadP, firmGenP, varGenP


    def getOptimizationBoundaries(self, SRCMethod, time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints):
        '''
        Determines the search space for the optimization using methods contained in initEstimate

        :param SRCMethod: [String] sets the SRC calculation method used from initEstimate.
        :param otherConstraints:
        :return:
        '''

        minESSPPa = 0
        maxESSPPa = 0
        minESSEPa = 0
        maxESSEPa = 0

        return minESSPPa, maxESSPPa, minESSEPa, maxESSEPa