#Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains the main flow of the optimization as it is to be called from the GBSController.

import os
import time

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs

from GBSAnalyzer.DataRetrievers.getBasecase import getBasecase
from GBSAnalyzer.DataRetrievers.getDataSubsets import getDataSubsets
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile
from GBSAnalyzer.PerformanceAnalyzers.getFuelUse import getFuelUse
from GBSAnalyzer.PerformanceAnalyzers.getPrimaryREContribution import getPrimaryREContribution
from GBSModel.generateRuns import generateRuns
from GBSModel.runSimulation0 import runSimulation
from GBSOptimizer.FitnessFunctions.getFitness import getFitness
from GBSOptimizer.OptimizationBoundaryCalculators.getOptimizationBoundaries import getOptimizationBoundaries


# DEV imports


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
        self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP, self.allGen, self.baseComponents = \
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
            self.fuelCurveDataPoints = pd.DataFrame(index = genFleet, columns = ['fuelCurve_pPu','fuelCurve_massFlow','POutMaxPa'])

            for genString in genFleet:
                genPath = os.path.join(self.rootProjectPath, 'InputData/Components/', genString + 'Descriptor.xml')
                genFile = open(genPath, 'r')
                genFileXML = genFile.read()
                genFile.close()
                genSoup = bs(genFileXML, "xml")

                self.fuelCurveDataPoints.loc[genString, 'fuelCurve_pPu'] = genSoup.fuelCurve.pPu.get('value')
                self.fuelCurveDataPoints.loc[genString, 'fuelCurve_massFlow'] = genSoup.fuelCurve.massFlow.get('value')
                self.fuelCurveDataPoints.loc[genString, 'POutMaxPa'] = genSoup.POutMaxPa.get('value')

            self.genAllFuelUsedBase, self.fuelStatsBase = getFuelUse(self.allGen, self.fuelCurveDataPoints)
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

        #print(self.optimizationConfig)



    def doOptimization(self):
        '''
        TODO implement and document
        :return:
        '''

        #print(self.searchMethod)

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

        maxIterNumber = int(float(self.optimizationConfig['maxRunNumber']))
        convergenceFlag = False

        # Select starting configuration at random, within the given bounds.
        # The power level can be chose freely between the previously determined bounds.
        self.essPPa = int(self.minESSPPa + (self.maxESSPPa - self.minESSPPa)*np.random.random_sample())
        # The energy capacity must meet at least the minimum duration requirement, and cannot exceed the maximum.
        self.essEPa = float(self.essPPa * (self.minESSEPa/self.minESSPPa) +
                 (self.maxESSEPa - (self.essPPa * (self.minESSEPa/self.minESSPPa))) * np.random.random_sample())

        print(['Initial guess: ESS P: ' + str(self.essPPa) + ' kW , ESS E: ' + str(self.essEPa) + ' kWh.'])

        # We want to make set numbers congruent with iteration numbers, a unique additional identifier needs to be added to the 'SetX' folder names.
        # We'll use current unix time to the second as the unique identifier. Thus, if the 'Set0' directory already
        # exists, we will name all directories of this optimization run as 'Set[IterationNumber].[snippetIdx].[identifier]', where
        # 'identifier' is the current unix time rounded to the nearest second.
        identifier = str(int(time.time()))


        # Get the index for the ESS to be added to the system
        essIdx = self.essExists()

        # Create bins for fitness tracking
        self.fitness = None
        fitnessLog = pd.DataFrame(index = pd.Index(range(0, maxIterNumber)), columns = ['fitness', 'essPPa', 'essEPa', 'bestFitness', 'bestP', 'bestE'])

        for iterIdx in range(0, maxIterNumber):
            #time.sleep(1)
            if not convergenceFlag:
                # Need the abbreviate data designators to retrieve start and stop time stamp indicies
                snippetIdx = self.abbrevDatasets.index.levels[0]
                setIdx = 0
                setPathList = list()
                setNameList = list()
                firmLoadsDF = pd.DataFrame()

                #Create setup file for each of the six simulations
                for sIdx in snippetIdx:
                    # Write the sets attributes, create the directory, etc.
                    startTimeIdx = self.abbrevDatasets.loc[sIdx].index[0]

                    endTimeIdx = self.abbrevDatasets.loc[sIdx].index[-1]

                    setPath, setName = self.setupSet(iterIdx, setIdx, identifier, essIdx, self.essPPa, self.essEPa, startTimeIdx, endTimeIdx)
                    setPathList.append(setPath)
                    setNameList.append(setName)
                    # Generate runs
                    generateRuns(setPath)

                    # Dispatch simulations
                    runSimulation(setPath)

                    # Pass through firm load data
                    firmLoadsDF['firmLoadP.' + str(setIdx)] = self.abbrevDatasets.loc[sIdx]['firmLoadP'][:-1].values
                    firmLoadsDF['firmLoadTime.' + str(setIdx)] = self.abbrevDatasets.loc[sIdx]['time'][:-1].values

                    setIdx = setIdx + 1


                    print('Iteration '+ str(iterIdx) +', Snippet ' + str(sIdx) + ' completed.')
                

                # Get KPIs
                # Collect data: we need to pull all the pertinent data for KPI calculation together from the results
                # in the set folders.
                self.resultsDF, resultsMetaInfo = self.collectResults(setPathList, setNameList)
                self.resultsDF = pd.concat([self.resultsDF, firmLoadsDF], axis = 1)
                
                # Get the new fitness value
                newFitness = getFitness(self.optimizationObjective, self.rootProjectPath, self.resultsDF, self.abbrevDatasetWeights, resultsMetaInfo)

                # Log progress
                fitnessLog['fitness'].loc[iterIdx] = newFitness
                fitnessLog['essPPa'].loc[iterIdx] = self.essPPa
                fitnessLog['essEPa'].loc[iterIdx] = self.essEPa


                # Get KPIs
                # TODO complete getRunMetaData(setPath, [0]) once getRunMetaData is completed. This might also be run then
                # prior to getFitness and save some effort.

                # Ascertain fitness
                # First iteration just write the values
                if not self.fitness:
                    self.fitness = newFitness
                    self.essPPaBest = self.essPPa
                    self.essEPaBest = self.essEPa

                    # Random next guess: The power level can be chose freely between the previously determined bounds.
                    self.essPPa = int(self.minESSPPa + (self.maxESSPPa - self.minESSPPa) * np.random.random_sample())
                    # The energy capacity must meet at least the minimum duration requirement, and cannot exceed the maximum.
                    self.essEPa = float(self.essPPa * (self.minESSEPa / self.minESSPPa) +
                                      (self.maxESSEPa - (self.essPPa * (
                                                  self.minESSEPa / self.minESSPPa))) * np.random.random_sample())

                    print(['Iteration: '+ str(iterIdx) + ', ESS P: ' + str(self.essPPa) + ' kW , ESS E: ' + str(self.essEPa) + ' kWh, Fitness: ' + str(self.fitness)])
                    # Set the improvement tracker
                    lastImprovement = 1

                # Other iterations check if fitness has improved (that is, has gotten smaller!!!)
                elif newFitness < self.fitness:
                    self.fitness = newFitness
                    self.essPPaBest = self.essPPa
                    self.essEPaBest = self.essEPa

                    self.essPPa, self.essEPa = self.getNextGuess(fitnessLog, self.essPPaBest, self.essEPaBest, iterIdx)

                    print(['Iteration: ' + str(iterIdx) + ', ESS P: ' + str(self.essPPa) + ' kW , ESS E: ' + str(
                        self.essEPa) + ' kWh, Fitness: ' + str(self.fitness)])

                    # Reset the improvement tracker
                    lastImprovement = 1


                # Lastly if nothing has improved search again in the previously defined range.
                else:
                    # Widen the random number deviation
                    self.essPPa, self.essEPa = self.getNextGuess(fitnessLog, self.essPPaBest, self.essEPaBest, iterIdx/lastImprovement) #np.sqrt(lastImprovement + 1))

                    # Increment the improvement tracker
                    lastImprovement = lastImprovement + 1

                    # If there's no improvement after X iterations in a row, terminate the algorithm.
                    # NOTE this can mean two things, either that we have achieved convergence, or that we're stuck somewhere
                    if lastImprovement > 10:
                        convergenceFlag = True
                        print('*********************************')
                        print('Terminated at Iteration: ' + str(iterIdx) + ' with fitness: ' + str(self.fitness))

                    print(['Iteration: ' + str(iterIdx) + ', ESS P: ' + str(self.essPPa) + ' kW , ESS E: ' + str(
                        self.essEPa) + ' kWh, Fitness: ' + str(self.fitness)])

                # Additional logging
                fitnessLog['bestFitness'].loc[iterIdx] = self.fitness
                fitnessLog['bestP'].loc[iterIdx] = self.essPPaBest
                fitnessLog['bestE'].loc[iterIdx] = self.essEPaBest

        self.fl = fitnessLog



    def getNextGuess(self, fl, pBest, eBest, iterNum):
        '''
        TODO document
        :param fl: fitnessLog
        :param pBest: essPPaBest: current best power guess for GBS
        :param eBest: essEPaBest: current best energy guess for GBS
        :param fBest: fitnessBest: current best fitness value.
        :return:
        '''

        fl = fl[['fitness', 'essPPa', 'essEPa']]
        fl = fl.dropna()

        # TODO make adjustable parameter
        exponent = 0.5

        # Calculate distance from best point
        fl['Dist'] = pd.Series(np.sqrt(list(np.asarray(fl['essPPa'] - pBest)**2 + np.asarray(fl['essEPa'] - eBest)**2)))
        fl = fl.sort_values('Dist')
        originFitness = fl['fitness'].iloc[0]
        originP = fl['essPPa'].iloc[0]
        originE = fl['essEPa'].iloc[0]
        print('Origin P: ' + str(originP) + ', Origin E: ' + str(originE))
        fl = fl[fl.Dist != 0]
        fl['Slope'] = (fl['fitness'] - originFitness)/fl['Dist']

        # Get the difference in power-coordinate DOWN the steepest gradient of the four nearest neighbors
        if fl.shape[0] < 3:
            maxSlopeIdx = fl['Slope'].idxmax()
        else:
            maxSlopeIdx = fl['Slope'][0:2].idxmax()

        dx = fl['essPPa'][maxSlopeIdx] - originP
        newCoord = originP - dx
        # Get random down and up variations from the power-coordinate
        rndDown = (newCoord - self.minESSPPa) * np.random.random_sample()/iterNum**exponent
        rndUp = (self.maxESSPPa - newCoord)*np.random.random_sample()/iterNum**exponent

        newESSPPa = float(newCoord - rndDown + rndUp)

        # Check constraints
        if newESSPPa < self.minESSPPa:
            newESSPPa = self.minESSPPa
        elif newESSPPa > self.maxESSPPa:
            newESSPPa = self.maxESSPPa

        # Get a random new value of energy storage capacity
        # Get the difference in power-coordinate DOWN the steepest gradient
        #maxSlopeIdx = fl.index[1]
        dy = fl['essEPa'][maxSlopeIdx] - originE
        newCoordY = originE - dy
        # Get random down and up variations from the power-coordinate
        # Note that ess needs to meet minimum duration requirement, so the minimum size is constraint by the currently
        # selected power level.
        currentESSEMin = newESSPPa * (self.minESSEPa/self.minESSPPa)
        rndDown = (newCoordY - currentESSEMin) * np.random.random_sample() / iterNum**exponent
        rndUp = (self.maxESSEPa - newCoordY) * np.random.random_sample() / iterNum**exponent

        newESSEPa = float(newCoordY - rndDown + rndUp)

        # Check constraints
        if newESSEPa < currentESSEMin:
            newESSEPa = currentESSEMin
        elif newESSEPa > self.maxESSEPa:
            newESSEPa = self.maxESSEPa


        return newESSPPa, newESSEPa


    def setupSet(self, iterIdx, setIdx, identifier, eesIdx, eesPPa, eesEPa, startTimeIdx, endTimeIdx):
        '''
        Generates the specific projectSetAttributes.xml file, and the necessary folder in the project's output folder.
        Returns the name of the specific set and it's absolute path. Set naming follows the convention of
        'Set[iterationNumber].[snippetNumber].[currentUNIXEpoch]', where iterationNumber is the current iteration of the
        of the optimizer, snippetNumber is the numerical identifier of the abbreviated data snippet, and the
        currentUNIXEpoch is the current local machine unix time to the second in int format.
        :param iterIdx: [int] current iteration of optimization algorithm
        :param setIdx: [int] numerical identifier of the snippet of time-series to be run here.
        :param identifier: [int] current local machine UNIX time to the second, could be any other integer
        :param eesIdx: [int] index of the ees to be added to the system, e.g., ees0. This is necessary should the system
            already have an ees that is not part of the optimization.
        :param eesPPa: [float] nameplate power capacity of the ees, assumed to be symmetrical in and out.
        :param eesEPa: [float] nameplate energy capacity of the ees, necessary to calculate ratedDuration, which is the
            actual parameter used in the setup.
        :param startTimeIdx: [int] index of the time stamp in the master-time series where the snippet of data starts
            that is to be run here.
        :param endTimeIdx: [int] index of the time stamp in the master-time series where the snippet of data ends that
            is to be run here.
        :return setPath: [os.path] path to the set folder
        :return setName: [String] name of the set
        '''

        # Get the current path to avoid issues with mkdir
        here = os.path.dirname(os.path.realpath(__file__))

        # * Create the 'SetAttributes' file from the template and the specific information given
        # Load the template
        setAttributeTemplatePath = os.path.join(here, '../GBSModel/Resources/Setup/projectSetAttributes.xml')
        setAttributeTemplateFile = open(setAttributeTemplatePath, 'r')
        setAttributeTemplateFileXML = setAttributeTemplateFile.read()
        setAttributeTemplateFile.close()
        setAttributeSoup = bs(setAttributeTemplateFileXML, 'xml')

        # Write the project name
        setAttributeSoup.project['name'] = self.projectName

        # Write the power levels and duration
        compNameVal = 'ees' + str(eesIdx) + ' ees' + str(eesIdx) + ' ees' + str(eesIdx)
        compTagVal = 'PInMaxPa POutMaxPa ratedDuration'
        compAttrVal = 'value value value'
        rtdDuration = int(3600*(eesEPa/eesPPa))
        compValueVal = str(eesPPa) + ' PInMaxPa.value ' + str(rtdDuration)

        setAttributeSoup.compAttributeValues.compName['value'] = compNameVal
        setAttributeSoup.compAttributeValues.find('compTag')['value'] = compTagVal  # See issue 99 for explanation
        setAttributeSoup.compAttributeValues.compAttr['value'] = compAttrVal
        setAttributeSoup.compAttributeValues.compValue['value'] = compValueVal

        # Write additional information regarding run-time, time resolution, etc.
        setupTagVal = 'componentNames runTimeSteps timeStep'
        setupAttrVal = 'value value value'
        componentNamesStr = 'ees' + str(eesIdx) + ',' + ','.join(self.baseComponents)
        setupValueVal = componentNamesStr + ' ' + str(startTimeIdx) + ',' + str(endTimeIdx) + ' ' + str(1)

        setAttributeSoup.setupAttributeValues.find('setupTag')['value'] = setupTagVal
        setAttributeSoup.setupAttributeValues.setupAttr['value'] = setupAttrVal
        setAttributeSoup.setupAttributeValues.setupValue['value'] = setupValueVal

        # Make the directory for this set
        setName = 'Set' + str(iterIdx) + '.' + str(setIdx) + '.' + str(identifier)
        setPath = os.path.join(self.rootProjectPath, 'OutputData/' + setName)
        os.mkdir(setPath)
        filename = self.projectName + setName + 'Attributes.xml'
        setPathName = os.path.join(setPath, filename)
        with open(setPathName, 'w') as xmlfile:
            xmlfile.write(str(setAttributeSoup))
        xmlfile.close()

        return setPath, setName


    def essExists(self):
        '''
        Checks if the system setup already contains one or more ESS components; looks for the largest index of those
        components, and returns the next available integer as the index for the ESS used in optimization.
        :return: essIdx
        '''
        # We also need to determine the unique name for the ess. Normally, this should be ess0. However, in the rare
        # situation that ess0 (and essX for that matter) already exists, we need to make sure we pick an available
        # numeric identifier
        # Load configuration from optimizerConfig<ProjectName>.xml
        setupFileName = self.projectName + 'Setup.xml'
        setupPath = os.path.join(self.rootProjectPath, 'InputData/Setup/', setupFileName)
        setupFile = open(setupPath, 'r')
        setupFileXML = setupFile.read()
        setupFile.close()
        setupSoup = bs(setupFileXML, "xml")

        components = setupSoup.componentNames.get('value').split()

        essComps = [comp for comp in components if comp.startswith('ees')]
        essNum = []
        for num in essComps:
            essNum.append(int(num[3:]))

        if not essNum:
            essNumMax = -1
        else:
            essNumMax = max(essNum)

        essIdx = essNumMax + 1

        return essIdx


    def collectResults(self, setPathList, setNameList):
        '''
        TODO document
        :param setPathList:
        :return resultsDF:
        '''
        # Get the current path to avoid issues with file locations
        #here = os.path.dirname(os.path.realpath(__file__))

        resultsDF = pd.DataFrame()

        for setIdx in range(0, len(setPathList)):
            # Get power channels for all components in the configuration
            # Get the component list from Attributes.xml file
            setAttrFile = open(os.path.join(setPathList[setIdx], self.projectName + setNameList[setIdx] + 'Attributes.xml'), 'r')
            setAttrXML = setAttrFile.read()
            setAttrFile.close()
            setAttrSoup = bs(setAttrXML, 'xml')

            setAttrVal = setAttrSoup.setupAttributeValues.setupValue.get('value')
            components = setAttrVal.split(' ')[0].split(',')

            for component in components:
                try:
                    ncChannel = readNCFile(os.path.join(setPathList[setIdx], 'Run0/OutputData/', component + 'P' + setNameList[setIdx] + 'Run0.nc'))
                    resultsDF[component + 'Time' + '.' + str(setIdx)] = pd.Series(np.asarray(ncChannel.time))
                    resultsDF[component + 'P' + '.' + str(setIdx)] = pd.Series(np.asarray(ncChannel.value))
                except Exception:
                    pass

            # Well also extract the list of generators used from the component list (needed for fuel calcs)
            genList = list()
            for component in components:
                if component[0:3] == 'gen':
                    genList.append(component)


        resultsMetaInfo = pd.DataFrame()
        resultsMetaInfo['setPathList'] = setPathList
        resultsMetaInfo['setNameList'] = setNameList
        resultsMetaInfo['genList'] = pd.Series(genList)
        resultsMetaInfo['snippetNum'] = pd.Series(len(setPathList))

        # The following parameters are added for test fitness function use.
        resultsMetaInfo['minESSPPa'] = self.minESSPPa
        resultsMetaInfo['maxESSPPa'] = self.maxESSPPa
        resultsMetaInfo['minESSEPa'] = self.minESSEPa
        resultsMetaInfo['maxESSEPa'] = self.maxESSEPa
        resultsMetaInfo['ESSPPa'] = self.essPPa
        resultsMetaInfo['ESSEPa'] = self.essEPa

        return resultsDF, resultsMetaInfo


    def plotProgress(self, fitnessLog, fitnessBest, essPPaBest, essEPaBest, otherInformation):
        x = np.asarray(fitnessLog['essPPa'][0:fitnessLog.shape[0]])
        x = x[np.isfinite(x)]
        y = np.asarray(fitnessLog['essPPa'][0:fitnessLog.shape[0]])
        y = y[np.isfinite(y)]



        # Potential well plotting
        xMin = otherInformation['minESSPPa'][0]
        xMax = otherInformation['maxESSPPa'][0]
        xMid = ((xMax - xMin) / 2) + xMin
        xCoord = np.linspace(xMin, xMax, 100)

        yMin = otherInformation['minESSEPa'][0]
        yMax = otherInformation['maxESSEPa'][0]
        yMid = ((yMax - yMin) / 2) + yMin
        yCoord = np.linspace(yMin, yMax, 100)

        XC, YC = np.meshgrid(xCoord, yCoord)

        # Use a parabolic well as the fitness, with goal to minimize
        fitnessWell = (XC - xMid) ** (2 * int(np.log10(YC) + 1)) + (YC - yMid) ** (2 * int(np.log10(XC) + 1))
