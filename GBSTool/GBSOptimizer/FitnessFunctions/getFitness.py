# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: May 20, 2018
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np
import os.path
import pandas as pd
from bs4 import BeautifulSoup as bs

from GBSAnalyzer.PerformanceAnalyzers.getFuelUse import getFuelUse
from GBSAnalyzer.PerformanceAnalyzers.getPrimaryREContribution import getPrimaryREContribution


def getMinFuelUtilizationFitness(rootProjectPath, inputDataFrame, otherInformation):
    '''
    Retrieves the fuel utilization for the input data. The rawFitness output is the total fuel in kg that has been
    consumed of the given time period of the time-series fed to GBSAnalzer.PerformanceAnalyzers.getFuelUse()

    :param rootProjectPath: [os.path] the root path to the project, necessary retrieve the correct configuration files
        for the generators, which contain their fuel curves.
    :param inputDataFrame: [DataFrame] contains the generator load and time channels required to calculate fuel use on
        the given time series.
    :param otherInformation: [DataFrame] contains meta-data such as the path to the pertinent Output folders which
        contain the specific setup files for the simulation run.
    :return rawFitness: [DataFrame] contains single value fitness [here total fuel use for each time series snippet] to
        be passed on to weighting and returned to the optimization method.
    '''

    snippetNum = otherInformation['snippetNum'][0]
    rawFitness = pd.DataFrame()
    setPath = otherInformation['setPathList'][0] # generators are the same for all sims in one iteration
    setName = otherInformation['setNameList'][0] # generators are the same for all sims in one iteration

    # Need to load fuel curves for this
    genFleet = list(otherInformation['genList'].dropna())
    fuelCurveDataPoints = pd.DataFrame(index=genFleet,
                                            columns=['fuelCurve_pPu', 'fuelCurve_massFlow', 'POutMaxPa'])

    # Retrieve the fuel curves for the generators involved
    # TODO: this is redundant to do every iteration, this data should be assembled once and passed on to this method via the otherInformation input.
    for genString in genFleet:
        genPath = os.path.join(rootProjectPath, 'OutputData/', setPath, 'Run0/Components/',
                               genString + setName + 'Run0Descriptor.xml')
        genFile = open(genPath, 'r')
        genFileXML = genFile.read()
        genFile.close()
        genSoup = bs(genFileXML, "xml")

        fuelCurveDataPoints.loc[genString, 'fuelCurve_pPu'] = genSoup.fuelCurve.pPu.get('value')
        fuelCurveDataPoints.loc[genString, 'fuelCurve_massFlow'] = genSoup.fuelCurve.massFlow.get('value')
        fuelCurveDataPoints.loc[genString, 'POutMaxPa'] = genSoup.POutMaxPa.get('value')

    # Construct correct allGen input
    for snippetIdx in range(0, int(round(snippetNum))):
        # Construct allGen for this snippet
        allGen = pd.DataFrame()
        # Need the time vector once
        timeVecAddedFlag = False
        for genName in genFleet:
            if not timeVecAddedFlag:
                allGen['time'] = inputDataFrame[genName + 'Time.' + str(snippetIdx)]
                timeVecAddedFlag = True
            allGen[genName + 'P'] = inputDataFrame[genName + 'P.' + str(snippetIdx)]

        # Call the fuel calculator
        genAllFuelUsed, fuelStats = getFuelUse(allGen, fuelCurveDataPoints)

        # Write results to rawFitness for further processing
        rawFitness['fitness' + str(snippetIdx)] = pd.Series(fuelStats['total'].loc['Fleet'])


    return rawFitness

def getMaxREContributionFitness(inputDataFrame, otherInformation):
    '''
    Pulls the renewable contribution to the firm load as the fitness value for each individual simulation in a given
    iteration.
    :param inputDataFrame: [DataFrame] contains all pertinent data from a given iteration. Channels (columns) are named
        canonically, with '.X' to denote which data snippet (i.e., MinLoad, MaxLoad, MinRE, etc.) run they belong to.
        Load data is also passed through from the initial datasubset as this should not change.
    :param otherInformation: [DataFrame] may contain various bits of meta information used by get<SOME>Fitness functions.
        Here only the number of snippets (snippetNum) is of interest.
    :return rawFitness: [DataFrame] contains one fitness value for each datasubset (snippet), these values are not weight
        in this module.
    '''

    snippetNum = otherInformation['snippetNum'][0]
    rawFitness = pd.DataFrame()

    for snippetIdx in range(0, int(round(snippetNum))):
        # Retrieve firmLoadP, firmGenP, and varGenP
        firmLoadP = inputDataFrame['firmLoadP.' + str(snippetIdx)]
        time = inputDataFrame['firmLoadTime.' + str(snippetIdx)]
        firmGenP = 0*firmLoadP.copy()
        varGenP = 0*firmLoadP.copy()
        for col in inputDataFrame.columns:
            if 'gen' in col and 'P' in col and '.' + str(snippetIdx) in col:
                firmGenP = firmGenP + inputDataFrame[col]
            elif 'wtg' in col and 'P' in col and '.' + str(snippetIdx) in col:
                varGenP = varGenP + inputDataFrame[col]

        subFitness = getPrimaryREContribution(time, firmLoadP, firmGenP, varGenP)
        # TODO the following inverting of values was moved from a previous spot, this needs to be tested.
        # in the next step we'll write 1/subfitness, as the optimizer searches for minima.
        rawFitness['fitness' + str(snippetIdx)] = 1/pd.Series(subFitness)

    return rawFitness

def weightedRawFitness(rawFitness, inputDataWeights, otherInformation):
    '''
    Uses the distribution of weights in inputDataWeights for the three load-based simulation and the three RE-based
    simulations and weights the six rawFitness values accordingly by multiplying each value by the respective weight
    and dividing by the total number of weights.  The final output (single fitness value) is the sum of all weighted
    raw fitnesses.
    :param rawFitness: [DataFrame] the rawFitness dataframe containing the individual fitness values from each individual
        simulation in an iteration.
    :param inputDataWeights: [DataFrame] the data weights that were calculated in getDataSubsets.
    :param otherInformation: [DataFrame] spare dataframe that could contain any additional constraints, here the total
        number of data snippets ('snippetNum') is the only value of interest.
    :return fitness: [float] returns a single value fitness
    '''

    snippetNum = otherInformation['snippetNum'][0]

    # check first if the inputDataWeights df is empty, if that is the case, the data for the simulations was not reduced
    # and no weighting is necessary
    if not inputDataWeights.empty:
        # for the loadBins (corresponding raw fitnesses are 0 through 2)
        loadFitnesses = inputDataWeights.loadBins.value_counts().sort_index()
        weightedFitness = rawFitness.copy()

        for indx in range(0, int(round(snippetNum/2))):
            # to avoid situations where not all bins have a count, we have to check if our iteration index is in the df index
            if indx in loadFitnesses.index:
                weightedFitness['fitness' + str(indx)][0] = loadFitnesses.loc[indx] * rawFitness['fitness' + str(indx)][0]
            else:
                weightedFitness['fitness' + str(indx)][0] = 0

        varGenFitnesses = inputDataWeights.varGenBins.value_counts().sort_index()
        for indx in range(int(round(snippetNum/2)), int(round(snippetNum))):
            # to avoid situations where not all bins have a count, we have to check if our iteration index is in the df index
            if indx-3 in varGenFitnesses.index:
                weightedFitness['fitness' + str(indx)][0] = varGenFitnesses.loc[indx-3] * rawFitness['fitness' + str(indx)][0]
            else:
                weightedFitness['fitness' + str(indx)][0] = 0

        totNumBins = loadFitnesses.sum() + varGenFitnesses.sum()

        fitness = weightedFitness.divide(totNumBins).sum().sum()

    # if the input data was not reduced, no weights are applied, but the fitness is just summed up
    else:
        fitness = rawFitness.sum().sum()

    return fitness


def getTestFitness(otherInformation):
        '''
        Contains two test functions (one commented out at any given time) to test convergence of optimization
        algorithms. Both functions are designed such that they have a known minimum.
        The parabolic function:
            f(x, y) = (x - x_0)^2 + 1000 * (y - y_0)^2,
        where, x is ESS Power and y is ESS Energy with x_0 and y_0 being the centers of the interval from the initial
        guesses provided by the methods of OptimizationBoundaryCalculators. If y is not orders of magnitude smaller than
        x, reducing the factor on the second term may be necessary. The minimum is f(x_0, y_0) = 0 and this is where the
        algorithm should converge to.

        The exponential function:
            f(x,y) = 1 - exp(-((x - x_0)/50)^2 - (0.5*(y - y_max))^2)
        where y_max is the upper end of the interval guessed by OptimizationBoundaryCalculators for energy capacity.
        This function is NOT centered on the intervals of P and E guessed, but rather the minimum at f(x_0,y_max) is
        pushed to the far end of the search space. As above, if orders of magnitude between P and E are not dissimilar,
        it might be necessary to change the factors for the two expressions in the exponential function.

        :param otherInformation:
        :return:
        '''
        x = otherInformation['ESSPPa'][0]
        xMin = otherInformation['minESSPPa'][0]
        xMax = otherInformation['maxESSPPa'][0]
        xMid = ((xMax - xMin)/2) + xMin
        print('xMid: ' + str(xMid))

        y = otherInformation['ESSEPa'][0]
        yMin = otherInformation['minESSEPa'][0]
        yMax = otherInformation['maxESSEPa'][0]
        yMid = ((yMax - yMin) / 2) + yMin
        print('yMid: ' + str(yMid))

        # Use a parabolic well as the fitness, with goal to minimize
        # Note this works with some difficulty - the function has a fairly flat and large plateau so near optimal
        # convergence can happen.
        fitness = (x - xMid)**2 + 1000*(y - yMid)**2

        # Exponential well
        #fitness = 1 - np.exp(-((x - xMid)/50)**2 - (0.5*(y - yMax))**2)
        print('x : ' + str(x) + ', y: ' + str(y)  + ', fit: ' + str(fitness))
        return fitness

def getFitness(fitnessMethod, rootProjectPath, inputDataFrame, inputDataWeights, otherInformation):
    '''
    Interface for actual fitness calculators. Selects fitness calculator based on 'fitnessMethod'. Handles the weighing
    of the data based on the weights given if needed and ensures that output is suited for a minimization problem.
    
    :param fitnessMethod: [String] fitness method to be used. This is the optimization objective.
    :param rootProjectPath: [os.path] path to the main project folder to keep track of configuration and result files
    :param inputDataFrame: [DataFrame] container of the time-series data used for fitness calculations. Typically
        contains multiple shorter data snippets.
    :param inputDataWeights: [DataFrame] the weights to be applied in the final fitness calculation to each of the above
        time-series snippets in inputDataFrame.
    :param otherInformation: [DataFrame] meta-data required to load correct configurations, know search boundaries, etc.
    :return fitness: [float] single value fitness. NOTE that this does not represent a necessarily realistic value like,
        e.g., renewable energy penetration, but something related.
    '''

    # TESTING remove below override for release.
    # fitnessMethod = 'testFunction'

    # Fitness method selection
    if fitnessMethod == 'minFuelUtilization':
        rawFitness = getMinFuelUtilizationFitness(rootProjectPath, inputDataFrame, otherInformation)

    elif fitnessMethod == 'maxREContribution':
        rawFitness = getMaxREContributionFitness(inputDataFrame, otherInformation)

    elif fitnessMethod == 'testFunction':
        # Just for testing algorithms NOT CONNECTED TO ACTUAL SIMULATION RESULTS
        rawFitness = getTestFitness(otherInformation)
        inputDataWeights = pd.DataFrame([])

        # Note: this one doesn't need to call weightedRawFitness() as no simulations were actually run.
    else:
        raise ImportError('Selected optimization objective, %s, is unknown.', fitnessMethod)

    # Calculate the weighted fitness from the input weights, and the raw fitness.
    fitness = weightedRawFitness(rawFitness, inputDataWeights, otherInformation)

    return fitness