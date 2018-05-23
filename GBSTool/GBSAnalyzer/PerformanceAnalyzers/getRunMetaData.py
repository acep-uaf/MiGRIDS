# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

import glob
# imports
import os
import sqlite3
import sys

import numpy as np
import pandas as pd

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile


def getRunMetaData(projectSetDir,runs):
    for runNum in runs:
        # get run dir
        projectRunDir = os.path.join(projectSetDir,'Run'+str(runNum))
        # get the set number
        dir_path = os.path.basename(projectSetDir)
        setNum = str(dir_path[3:])

        # go to dir where output files are saved
        os.chdir(os.path.join(projectRunDir, 'OutputData'))

        # load the total powerhouse output
        genPStats, genP, ts = loadResults('powerhousePSet'+str(setNum)+'Run'+str(runNum)+'.nc')
        # get generator power available stats
        genPAvailStats, genPAvail, ts = loadResults('genPAvailSet'+str(setNum)+'Run' + str(runNum) + '.nc')

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
        wtgPImportStats, wtgPImport, ts = loadResults('wtgPImportSet'+str(setNum)+'Run' + str(runNum) + '.nc')
        wtgPAvailStats, wtgPAvail, ts = loadResults('wtgPAvailSet'+str(setNum)+'Run' + str(runNum) + '.nc')
        wtgPchStats, wtgPch, ts = loadResults('wtgPchSet'+str(setNum)+'Run' + str(runNum) + '.nc')

        # spilled wind power in kWh
        wtgPspillTot = (wtgPAvailStats[4] - wtgPImportStats[4] - wtgPchStats[4])/3600

        # imported wind power in kWh
        wtgPImportTot = wtgPImportStats[4]/3600

        # windpower used to charge EESS in kWh
        wtgPchTot = wtgPchStats[4]/3600

        # eess
        # get eess power
        eessPStats, eessP, ts = loadResults('eessPSet'+str(setNum)+'Run' + str(runNum) + '.nc')
        # get the charging power
        eessPch = [x for x in eessP if x < 0]
        eessPchTot = -sum(eessPch)*ts/3600 # total kWh chargning of eess
        # get the discharging power
        eessPdis = [x for x in eessP if x > 0]
        eessPdisTot = (sum(eessPdis) * ts)/3600  # total kWh dischargning of eess
        # get eess SRC
        # get all ees used in kWh
        eessSRCTot = 0
        for eesFile in glob.glob('ees*SRC*.nc'):
            eesSRCStats, eesSRC, ts = loadResults(eesFile)
            eessSRCTot += eesSRCStats[4]/3600

        # TODO: add gen charging and fuel consumption
        # create df from generator nc files
        # get all gen power files
        '''
        dfGenP = 0
        for idx, genPFile in enumerate(glob.glob('gen*PSet*.nc')):
            genPStats, genP, genTime = loadResults(genPFile,returnTimeSeries=True) # load the file
            if idx == 0: # if the first, initiate df
                dfGenP = pd.DataFrame([genTime,genP],columns=['time',str(idx)])
            else:
                dfGenP[str(idx)] = genP # assign new column 
            '''

        # save into SQL db
        os.chdir(projectSetDir)
        conn = sqlite3.connect('set' + str(setNum) + 'Results.db')
        # check if table exists, tableName will be empty if not
        tableName = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name='Results';", conn)
        # if not initialized
        if tableName.empty:
            # create
            df = pd.DataFrame(columns = ['Generator Import kWh','Generator Charging kWh','Generator Switching','Generator Loading','Generator Fuel Consumption kg','Wind Power Import kWh','Wind Power Spill kWh','Wind Power Charging kWh','Energy Storage Discharge kWh','Energy Storage Charge kWh','Energy Storage SRC kWh'])
        else:
            df = pd.read_sql_query('select * from Results',conn)
        # add row for this run
        df.loc[runNum] = [genPTot,0,genSw,genLoadingMean,0,wtgPImportTot,wtgPspillTot,wtgPchTot,eessPdisTot,eessPchTot,eessSRCTot]
        df.to_sql('Results', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        conn.close()
        df.to_csv('Set' + str(setNum) + 'Results.csv') # save a csv version



    # get the stats for this variable
def loadResults(fileName, location = '', returnTimeSeries = False):
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

    if returnTimeSeries is False:
        return [valMean, valSTD, valMax, valMin, valInt], val, timeStep
    else:
        return [valMean, valSTD, valMax, valMin, valInt], val, var.time
