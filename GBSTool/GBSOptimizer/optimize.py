#Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains the main flow of the optimization as it is to be called from the GBSController.

import os

import pandas as pd
from bs4 import BeautifulSoup as bs

from GBSAnalyzer.DataRetrievers.getBasecase import getBasecase
from GBSAnalyzer.DataRetrievers.getDataSubsets import getDataSubsets
from GBSAnalyzer.PerformanceAnalyzers.getFuelUse import getFuelUse
from GBSAnalyzer.PerformanceAnalyzers.getPrimaryREContribution import getPrimaryREContribution
from GBSOptimizer.OptimizationBoundaryCalculators.getOptimizationBoundaries import getOptimizationBoundaries


class optimize:
    '''
    TODO: document this
    '''

    def __init__(self, projectName, inputArgs):
        '''
        Constructor: does all necessary setup for the optimization itself.

        :param projectName: [String] name of the project, used to locate project folder tree within the GBSProject
            folder structure
        :param inputArgs: [Array of strings] spare input, currently un-used.
        '''

        # Setup key parameters
        self.thisPath = os.path.dirname(os.path.realpath(__file__))
        self.projectName = projectName
        self.rootProjectPath = os.path.join(self.thisPath, '../../GBSProjects/', self.projectName) # root path to project files relative to this file location

        # Load configuration from optimizerConfig<ProjectName>.xml
        configFileName = 'optimizerConfig' + self.projectName + '.xml'
        configPath = os.path.join(self.rootProjectPath, 'InputData/Setup/', configFileName)
        configFile = open(configPath, 'r')
        configFileXML = configFile.read()
        configFile.close()
        configSoup = bs(configFileXML, "xml")

        self.searchMethod = configSoup.optimizationMethod.get('value')
        self.optimizationObjective = configSoup.optimizationObjective.get('value')
        self.dataReductionMethod = configSoup.dataReductionMethod.get('value')  # should be 'RE-load-one-week'
        self.boundaryMethod = configSoup.optimizationEnvelopeEstimator.get('value')     # should be 'variableSRC'

        # Bins for reference parameters and current best performing
        # both will be written below with actual initial values, but are placed here so they don't get lost
        self.basePerformance = 0
        self.currentBestPerformance = 0

        # Retrieve data from base case (Input files)
        self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP, self.allGen = \
            getBasecase(self.projectName, self.rootProjectPath)


        # Calculate boundaries for optimization search
        # Get boundary constraints from config file, since this may vary from method to method, these are then lumped
        # into a list 'constraints' that is passed through to the appropriate algorithm
        opBndMethodConfig = configSoup.find(self.boundaryMethod + 'Config')
        opBndMethodConfigChildren = opBndMethodConfig.findChildren()
        constraints = list()
        for child in opBndMethodConfigChildren:
            constraints.append(child.get('value'))

        self.minESSPPa, self.maxESSPPa, self.minESSEPa, self.maxESSEPa = \
            getOptimizationBoundaries(self.boundaryMethod, self.time, self.firmLoadP, self.varLoadP, self.firmGenP,
                                      self.varGenP, constraints)

        # Get the short test time-series
        # TODO remove following line, which just adjusts time stamps for prototyping prior to release
        self.time = self.time/1e9

        reductionInput = \
            pd.DataFrame({'time':self.time, 'firmLoadP':self.firmLoadP, 'varGenP':self.varGenP})#, index=self.time)

        self.abbrevDatasets, self.abbrevDatasetWeights = getDataSubsets(reductionInput, self.dataReductionMethod)

        # Setup optimization runs
        # Branch based on input from 'configSoup'->optimizationObjective
        # Get base case KPI based on optimization objective
        # Any of the following if-branches needs to write to self.basePerformance with the reference KPI based on the
        # optimization objective
        if self.optimizationObjective == 'maxREContribution':
            # Calculate base case RE contribution
            self.basePerformance = getPrimaryREContribution(self.time, self.firmLoadP, self.firmGenP, self.varGenP)

        elif self.optimizationObjective == 'minFuelUtilization':
            # Calculate base case fuel consumption
            # Need to load fuel curves for this
            genFleetList = list(self.allGen.columns.values)
            genFleetList.remove('time')
            genFleet = list()
            for gen in genFleetList:
                genFleet.append(gen[:-1])
            fuelCurveDataPoints = pd.DataFrame(index = genFleet, columns = ['fuelCurve_pPu','fuelCurve_massFlow','POutMaxPa'])

            for genString in genFleet:
                genPath = os.path.join(self.rootProjectPath, 'InputData/Components/', genString + 'Descriptor.xml')
                genFile = open(genPath, 'r')
                genFileXML = genFile.read()
                genFile.close()
                genSoup = bs(genFileXML, "xml")

                fuelCurveDataPoints.loc[genString, 'fuelCurve_pPu'] = genSoup.fuelCurve.pPu.get('value')
                fuelCurveDataPoints.loc[genString, 'fuelCurve_massFlow'] = genSoup.fuelCurve.massFlow.get('value')
                fuelCurveDataPoints.loc[genString, 'POutMaxPa'] = genSoup.POutMaxPa.get('value')

            self.genAllFuelUsedBase, self.fuelStatsBase = getFuelUse(self.allGen, fuelCurveDataPoints)
            self.basePerformance = self.fuelStatsBase['total']
        else:
            raise ValueError('Unknown optimization objective, %s, selected.' % self.optimizationObjective)

        # Since we do not have a better performing set of sims yet, make basePerformance best performing.
        self.currentBestPerformance = self.basePerformance

        # Retrieve additional optimization config arguments for the selected algorithm
        self.optimizationConfig = dict()
        opAlgConfig = configSoup.find(self.searchMethod + 'Config')
        opAlgConfigChildren = opAlgConfig.findChildren()
        for child in opAlgConfigChildren:
            self.optimizationConfig[child.name] = child.get('value')

        print(self.optimizationConfig)



    def doOptimization(self):
        '''
        TODO implement and document
        :return:
        '''

        if self.searchMethod == 'hillClimber':
            # call hillClimber function
            self.hillClimber()

        # FUTUREFEATURE: add further optimization methods here
        else:
            raise ValueError('Unknown optimization method, %s, selected.' % self.searchMethod)


    def hillClimber(self):
        '''
        TODO implement and document
        :return:
        '''

        maxRunNumber = int(float(self.optimizationConfig['maxRunNumber']))

        for