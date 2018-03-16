# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import os
import sys
import numpy as np
import glob
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile
from GBSAnalyzer.PerformanceAnalyzers.getFuelUse import getFuelUse

def getRunMetaData(projectRunDir):
    # get run number
    dir_path = os.path.basename(projectRunDir)
    runNum = int(dir_path[3:])
    # get the set number
    os.chdir(projectRunDir)
    os.chdir('..')
    dir_path = os.path.basename(os.getcwd())
    setNum = int(dir_path[3:])

    # go to dir where output files are saved
    os.chdir(os.path.join(projectRunDir, 'OutputData'))

    # load the total powerhouse output
    genPStats, genP, ts = loadResults('genPRun'+str(runNum)+'.nc')
    # get generator power available stats
    genPAvailStats, genPAvail, ts = loadResults('genPAvailRun' + str(runNum) + '.nc')

    # calculate the average loading while online
    idxOnline = [idx for idx, x in enumerate(genPAvail) if x >0] # the indices of when online
    # the loading profile of when online
    genLoading = [x/genPAvail[idxOnline[idx]] for idx, x in enumerate(genP[idxOnline])]
    genLoadingMean = np.mean(genLoading)
    genLoadingStd = np.std(genLoading)
    genLoadingMax = np.max(genLoading)
    genLoadingMin = np.min(genLoading)

    # calculate total generator energy delivered in kWh
    genPTot = genPStats[4]/3600

    # calculate generator switching
    genSw = np.count_nonzero(np.diff(genPAvail))

    # load the wind data
    wtgPImportStats, wtgPImport, ts = loadResults('wtgPImportRun' + str(runNum) + '.nc')
    wtgPAvailStats, wtgPAvail, ts = loadResults('wtgPAvailRun' + str(runNum) + '.nc')
    wtgPchStats, wtgPch, ts = loadResults('wtgPchRun' + str(runNum) + '.nc')

    # spilled wind power in kWh
    wtgPspill = (wtgPAvailStats[4] - wtgPImportStats[4] - wtgPchStats[4])/3600

    # imported wind power in kWh
    wtgPImportTot = wtgPImportStats[4]/3600

    # windpower used to charge EESS in kWh
    wtgPchTot = wtgPchStats[4]/3600

    # eess
    # get eess power
    eessPStats, eessP, ts = loadResults('eessPRun' + str(runNum) + '.nc')
    # get the charging power
    eessPch = [x for x in eessP if x < 0]
    eessPchTot = sum(eessPch)*ts # total kWs chargning of eess
    # get the discharging power
    eessPdis = [x for x in eessP if x > 0]
    eessPdisTot = sum(eessPdis) * ts  # total kWs chargning of eess
    # get eess SRC
    # get all ees used in kWh
    eessSRCTot = 0
    for eesFile in glob.glob('ees*SRC*.nc'):
        eesSRCStats, eesSRC, ts = loadResults(eesFile)
        eessSRCTot += eesSRCStats[4]/3600

    # save into SQL db



    # get the stats for this variable
def loadResults(fileName, location = ''):
    if location != '':
        os.chdir(location)
    var = readNCFile(fileName)
    val = np.array(var.value)*var.scale + var.offset
    timeStep = np.mean(np.diff(var.time)) # mean timestep in seconds
    valMean = np.mean(val)
    valSTD = np.std(val)
    valMax = np.max(val)
    valMin = np.min(val)
    valInt = sum(val)*timeStep # the integral over seconds. If the value is in kW, this is kWs.

    return [valMean, valSTD, valMax, valMin, valInt], val, timeStep
