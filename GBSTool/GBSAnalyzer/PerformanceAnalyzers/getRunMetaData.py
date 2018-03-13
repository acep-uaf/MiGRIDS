# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import os
import sys
import numpy as np
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile

def getRunMetaData(projectDir, run):
    # go to dir where output files are saved
    os.chdir(os.path.join(projectDir, 'OutputData', 'Run' + str(run)))

    # diesel generators
    # get generator power
    genPStats, genP = loadResults('genPRun'+str(run)+'.nc')
    # get generator power available stats
    genPAvailStats, genPAvail = loadResults('genPAvailRun'+str(run)+'.nc')
    # calculate the mean loading on gen
    genLoadingMean = genPStats[0]/genPAvailStats[0]
    # calculate the gen switching
    genSw = sum(np.abs(np.diff(genPAvail)))

    # wind turbines
    # get wtg import power
    wtgPImportStats = loadResults('wtgPImportRun' +  str(run) + '.nc')
    wtgPAvailStats = loadResults('wtgPAvailRun' +  str(run) + '.nc')
    wtgPchStats = loadResults('wtgPchRun' +  str(run) + '.nc')
    # get spill stats
    wtgPspillTot = wtgPAvailStats[0] - wtgPImportStats[0] - wtgPchStats[0]
    wtgPspillMean = wtgPAvailStats[1] - wtgPImportStats[1] - wtgPchStats[1]
'''
    # eess
    # get eess power
    # get all ees used
    eesFiles = os.listdir('ees*Dis*.nc')
    for eesFile in eesFiles:
        # get eesID
        eesID = eesFiles[]
    eessPStats = loadResults()

'''

    # get the stats for this variable
def loadResults(fileName, location = ''):
    if location != '':
        os.chdir(location)
    var = readNCFile(fileName)
    val = np.array(var.value)*var.scale + var.offset
    valTot = sum(val)
    valMean = np.mean(val)
    valSTD = np.std(val)
    valMax = np.max(val)
    valMin = np.min(val)

    return (valTot, valMean, valSTD, valMax, valMin), val
