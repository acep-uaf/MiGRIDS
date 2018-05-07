#Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains the main flow of the optimization as it is to be called from the GBSController.

import os

import pandas as pd

from GBSAnalyzer.DataRetrievers.getBasecase import getBasecase
from GBSAnalyzer.DataRetrievers.getDataSubsets import getDataSubsets
from GBSOptimizer.OptimizationBoundaryCalculators.getOptimizationBoundaries import getOptimizationBoundaries


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
        self.rootProjectPath = os.path.join(self.thisPath, '../../GBSProjects/', self.projectName) # root path to project files relative to this file location
        self.searchMethod = searchArgs[0]
        self.optimizationObjective = searchArgs[1]
        self.dataReductionMethod = searchArgs[2]  # should be 'RE-load-one-week'
        self.boundaryMethod = searchArgs[3]     # should be 'variableSRC'

        # Retrieve data from base case (Input files)
        print(self.rootProjectPath)
        self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP = \
            getBasecase(self.projectName, self.rootProjectPath)

        # Calculate boundaries for optimization search
        # TODO get boundary constraints from config
        self.minESSPPa, self.maxESSPPa, self.minESSEPa, self.maxESSEPa = \
            getOptimizationBoundaries(self.boundaryMethod, self.time, self.firmLoadP, self.varLoadP, self.firmGenP,
                                      self.varGenP, ['0.15', '60', '0.7', '0.99', '1.15'])

        # Get the short test time-series
        # TODO remove following line, which just adjusts time stamps for prototyping prior to release
        self.time = self.time/1e9

        reductionInput = \
            pd.DataFrame({'time':self.time, 'firmLoadP':self.firmLoadP, 'varGenP':self.varGenP})#, index=self.time)

        self.abbrevDatasets, self.abbrevDatasetWeights = getDataSubsets(reductionInput, self.dataReductionMethod)

        # Setup optimization runs
        # Branch based on input from 'searchArgs'
        # NOTE: we need to get the KPI for the base case somewhere here to compare results against
        if self.searchMethod == 'simulatedAnnealing':
            # call simualtedAnnealing functions
            a = 0
        # FUTUREFEATURE: add further optimization methods here
        else:
            raise ValueError('Unknown optimization method, %s, selected.' % searchArgs[0])



'''
    def getOptimizationBoundaries(self, SRCMethod, time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints):
        ''''''
        Determines the search space for the optimization using methods contained in initEstimate

        :param SRCMethod: [String] sets the SRC calculation method used from initEstimate.
        :param otherConstraints:
        :return:
        ''''''

        minESSPPa = 0
        maxESSPPa = 0
        minESSEPa = 0
        maxESSEPa = 0

        return minESSPPa, maxESSPPa, minESSEPa, maxESSEPa'''