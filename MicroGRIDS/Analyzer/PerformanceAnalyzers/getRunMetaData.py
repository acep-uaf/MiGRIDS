# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

import glob
# imports
import os
import sqlite3
import sys
import re
import numpy as np
import pandas as pd
import pickle

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from Analyzer.DataRetrievers.readNCFile import readNCFile
from Analyzer.DataRetrievers.readXmlTag import readXmlTag


def getRunMetaData(projectSetDir,runs):
    # get the set number
    dir_path = os.path.basename(projectSetDir)
    setNum = str(dir_path[3:])

    # read the input parameter sql database
    os.chdir(projectSetDir)
    conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db')
    # get the attributes
    dfAttr = pd.read_sql_query('select * from compAttributes', conn)
    conn.close()

    # add columns for results
    df = pd.DataFrame(
        columns=['Generator Import kWh', 'Generator Charging kWh', 'Generator Switching', 'Generator Loading', 'Generator Online Capacity',
                 'Generator Fuel Consumption kg', 'Diesel-off time h', 'Generator Cumulative Run time h', 'Generator Cumulative Capacity Run Time kWh', 'Generator Overloading Time h','Generator Overloading kWh',
                 'Wind Power Import kWh', 'Wind Power Spill kWh',
                 'Wind Power Charging kWh', 'Energy Storage Discharge kWh', 'Energy Storage Charge kWh',
                 'Energy Storage SRC kWh', 'Energy Storage Overloading Time h','Energy Storage Overloading kWh','Thermal Energy Storage Throughput kWh'])

    genOverLoading = []
    eessOverLoading = []
    for runNum in runs:
        # get run dir
        projectRunDir = os.path.join(projectSetDir,'Run'+str(runNum))

        # go to dir where output files are saved
        os.chdir(os.path.join(projectRunDir, 'OutputData'))

        # load the total powerhouse output
        genPStats, genP, ts = loadResults('powerhousePSet'+str(setNum)+'Run'+str(runNum)+'.nc')
        # load the total powerhouse charging of eess
        genPchStats, genPch, ts = loadResults('powerhousePchSet' + str(setNum) + 'Run' + str(runNum) + '.nc')
        # get generator power available stats
        genPAvailStats, genPAvail, tsGenPAvail = loadResults('genPAvailSet'+str(setNum)+'Run' + str(runNum) + '.nc')

        # calculate the average loading while online
        idxOnline = [idx for idx, x in enumerate(genPAvail) if x >0] # the indices of when online
        # the loading profile of when online
        genLoading = [x/genPAvail[idxOnline[idx]] for idx, x in enumerate(genP[idxOnline])]
        genLoadingMean = np.mean(genLoading)
        genLoadingStd = np.std(genLoading)
        genLoadingMax = np.max(genLoading)
        genLoadingMin = np.min(genLoading)
        # the online capacity of diesel generators
        genCapacity = genPAvail[idxOnline]
        genCapacityMean = np.mean(genCapacity)

        # get overloading of diesel
        # get indicies of when diesel generators online
        idxGenOnline = genPAvail > 0
        genOverLoadingTime = np.count_nonzero(genP[idxGenOnline]>genPAvail[idxGenOnline]) * ts/3600
        genLoadingDiff = genP[idxGenOnline] - genPAvail[idxGenOnline]
        genOverLoading = genOverLoading + [[x for x in genLoadingDiff if x > 0]]
        genOverLoadingkWh = sum(genLoadingDiff[genLoadingDiff>0]) * ts / 3600

        # get overloading of the ESS. this is the power requested from the diesel generators when none are online.
        # to avoid counting instances where there there is genP due to rounding error, only count if greater than 1
        eessOverLoadingTime = sum([1 for x in genP[~idxGenOnline] if abs(x) > 1])* ts/3600
        eessOverLoadingkWh = sum([abs(x) for x in genP[~idxGenOnline] if abs(x) > 1])*ts/3600
        eessOverLoading = eessOverLoading + [[x for x in genP[~idxGenOnline] if abs(x) > 1]]

        # get the total time spend in diesel-off
        genTimeOff = np.count_nonzero(genPAvail == 0)* tsGenPAvail / 3600

        # get the total diesel run time
        genTimeRunTot = 0.
        genRunTimeRunTotkWh = 0.
        for genRunTimeFile in glob.glob('gen*RunTime*.nc'):
            genRunTimeStats, genRunTime, ts = loadResults(genRunTimeFile)
            genTimeRunTot += np.count_nonzero(genRunTime != 0)* ts / 3600
            # get the capcity of this generator
            # first get the gen ID
            genID = re.search('gen(.*)RunTime',genRunTimeFile).group(1)
            genPMax = readXmlTag("gen"+genID +"Set"+str(setNum)+"Run"+str(runNum)+"Descriptor.xml", "POutMaxPa",
                                 "value", fileDir=projectRunDir+"/Components", returnDtype='float')
            genRunTimeRunTotkWh += (np.count_nonzero(genRunTime != 0)* ts / 3600)*genPMax[0]

        # calculate total generator energy delivered in kWh
        genPTot = (genPStats[4] - genPchStats[4])/3600

        # calculate total generator energy delivered in kWh
        genPch = (genPchStats[4]) / 3600

        # calculate generator switching
        genSw = np.count_nonzero(np.diff(genPAvail))

        # load the wind data
        wtgPImportStats, wtgPImport, ts = loadResults('wtgPImportSet'+str(setNum)+'Run' + str(runNum) + '.nc')
        wtgPAvailStats, wtgPAvail, ts = loadResults('wtgPAvailSet'+str(setNum)+'Run' + str(runNum) + '.nc')
        wtgPchStats, wtgPch, ts = loadResults('wtgPchSet'+str(setNum)+'Run' + str(runNum) + '.nc')

        # tes
        # get tess power, if included in simulations
        if len(glob.glob('ees*SRC*.nc')) > 0:
            tessPStats, tessP, ts = loadResults('tessP' + str(setNum) + 'Run' + str(runNum) + '.nc')
            tessPTot = tessPStats[4] / 3600
        else:
            tessPStats = [0, 0, 0, 0, 0]

        # spilled wind power in kWh
        wtgPspillTot = (wtgPAvailStats[4] - wtgPImportStats[4] - wtgPchStats[4] - tessPStats[4])/3600

        # imported wind power in kWh
        wtgPImportTot = wtgPImportStats[4]/3600

        # windpower used to charge EESS in kWh
        wtgPchTot = wtgPchStats[4]/3600

        # eess
        # get eess power
        eessPStats, eessP, ts = loadResults('eessPSet'+str(setNum)+'Run' + str(runNum) + '.nc')
        # get the charging power
        eessPch = [x for x in eessP if x < 0]
        eessPchTot = -sum(eessPch)*ts/3600 # total kWh charging of eess
        # get the discharging power
        eessPdis = [x for x in eessP if x > 0]
        eessPdisTot = (sum(eessPdis) * ts)/3600  # total kWh dischargning of eess
        # get eess SRC
        # get all ees used in kWh
        eessSRCTot = 0
        for eesFile in glob.glob('ees*SRC*.nc'):
            eesSRCStats, eesSRC, ts = loadResults(eesFile)
            eessSRCTot += eesSRCStats[4]/3600






        # TODO: add gen fuel consumption
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
        '''

        # add row for this run
        df.loc[runNum] = [genPTot,genPch,genSw,genLoadingMean,genCapacityMean,None,genTimeOff,genTimeRunTot,genRunTimeRunTotkWh,genOverLoadingTime,genOverLoadingkWh,wtgPImportTot,wtgPspillTot,wtgPchTot,eessPdisTot,eessPchTot,eessSRCTot,eessOverLoadingTime,eessOverLoadingkWh,tessPTot]

    dfResult = pd.concat([dfAttr, df], axis=1, join='inner')

    os.chdir(projectSetDir)
    conn = sqlite3.connect('set' + str(setNum) + 'Results.db')
    dfResult.to_sql('Results', conn, if_exists="replace", index=False)  # write to table compAttributes in db
    conn.close()
    dfResult.to_csv('Set' + str(setNum) + 'Results.csv')  # save a csv version

    # make pdfs
    # generator overloading
    # get all simulations that had some generator overloading
    genOverloadingSims = [x for x in genOverLoading if len(x)>0]
    if len(genOverloadingSims) > 0:
        maxbin = max(max(genOverloadingSims))
        minbin = min(min(genOverloadingSims))
        genOverLoadingPdf = [[]]*len(genOverLoading)
        for idx, gol in enumerate(genOverLoading):
            genOverLoadingPdf[idx] = np.histogram(gol,10,range=(minbin,maxbin))
    else:
        genOverLoadingPdf = []
    outfile = open('genOverLoadingPdf.pkl','wb')
    pickle.dump(genOverLoadingPdf,outfile)
    outfile.close()

    # eess overloading
    eessOverLoadingSims = [x for x in eessOverLoading if len(x) > 0]
    if len(eessOverLoadingSims) > 0:
        maxbin = max(max(eessOverLoadingSims))
        minbin = min(min(eessOverLoadingSims))
        eessOverLoadingPdf = [[]] * len(eessOverLoading)
        for idx, eol in enumerate(eessOverLoading):
            eessOverLoadingPdf[idx] = np.histogram(eol, 10, range=(minbin, maxbin))
    else:
        eessOverLoadingPdf = []
    outfile = open('eessOverLoadingPdf.pkl', 'wb')
    pickle.dump(eessOverLoadingPdf, outfile)
    outfile.close()


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
