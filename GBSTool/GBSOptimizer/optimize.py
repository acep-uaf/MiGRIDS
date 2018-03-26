#Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains the main flow of the optimization as it is to be called from the GBSController.

import os
from distutils.util import strtobool

import pandas as pd
from bs4 import BeautifulSoup as soup

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
        # TODO: implement retrieving data from base case, or dispatch base case calculation if it doesn't exist, or use input files as base case
        self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP = self.getBasecase()

        # Calculate boundaries for optimization search
        self.minESSPPa, self.maxESSPPa, self.minESSEPa, self.maxESSEPa = \
            self.getOptimizationBoundaries(self.boundaryMethod, self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP, otherConstraints=None)

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
        # Empty bins
        varLoadP = []
        firmGenP = []
        varGenP = []
        
        # Read project meta data to get (a) all loads, (b) all generation, and their firm and variable subsets.
        setupMetaHandle = open(os.path.join(rootProjectPath, 'InputData/Setup/' + projectName + 'Setup.xml'), 'r')
        setupMetaData = setupMetaHandle.read()
        setupMetaHandle.close()
        setupMetaSoup = soup(setupMetaData, 'xml')

        # Retrieve the time and firm load vectors
        firmLoadPFileName = setupMetaSoup.loadProfileFile.get('value')
        firmLoadPFile = readNCFile(os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/' + firmLoadPFileName))
        time = pd.Series(firmLoadPFile.time)
        firmLoadP = pd.Series((firmLoadPFile.value + firmLoadPFile.offset)*firmLoadPFile.scale)

        # Setup other data channels
        firmGenP = pd.Series(firmLoadP.copy()*0)
        varGenP = pd.Series(firmLoadP.copy()*0)

        # Get list if all components
        components = setupMetaData.componentNames.get('value').split()
        # Step through the given list of components and assign them to the correct data channel if appropriate
        for cpt in components:
            # load meta data for the component
            cptMetaHandle = open(os.path.join(rootProjectPath, 'InputData/Components/' + cpt +'Descriptor.xml'), 'r')
            cptMetaData = cptMetaHandle.read()
            cptMetaHandle.close()
            cptMetaSoup = soup(cptMetaData, 'xml')

            # Read the type, if it is a source it is going into one of the generation channels
            if cptMetaSoup.type.get('value') == 'source':
                # Load associated time series
                chName = cptMetaSoup.component.get('name') + 'P.nc'
                fgPHandle = readNCFile(
                    os.path.join(rootProjectPath, 'InputData/TimeSeriesData/ProcessedData/' + chName))
                # Check if it can load follow, if true add it to the firmGenP channel
                if strtobool(cptMetaSoup.isLoadFollowing.get('value')):
                    firmGenP = firmGenP + pd.Series((fgPHandle.value + fgPHandle.offset) * fgPHandle.scale)
                # If it cannot load follow, it is a variable generator
                else: # not strtobool(cptMetaSoup.isLoadFollowing.get('value'))
                    varGenP = varGenP + pd.Series((fgPHandle.value + fgPHandle.offset) * fgPHandle.scale)

            # TODO - handle varLoadP


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