# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 28, 2018
# License: MIT License (see LICENSE file of this package for more information)

import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here,".."))
import sqlite3
# add to sys path

import tkinter as tk
from tkinter import filedialog

import pandas as pd

from GBSModel.SystemOperations import SystemOperations

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
sys.path.append(here)
from GBSAnalyzer.DataRetrievers.readXmlTag import readXmlTag
from GBSAnalyzer.DataWriters.writeNCFile import writeNCFile


def runSimulation(projectSetDir = ''):

    if projectSetDir == '':
        print('Choose the project directory')
        root = tk.Tk()
        root.withdraw()
        projectSetDir = filedialog.askdirectory()

    # get set number
    dir_path = os.path.basename(projectSetDir)
    setNum = str(dir_path[3:])
    # get the project name
    os.chdir(projectSetDir)
    os.chdir('../..')
    projectDir = os.getcwd()
    projectName = os.path.basename(projectDir)
    # timeseries directory
    timeSeriesDir = os.path.join(projectDir,'InputData','TimeSeriesData','ProcessedData')

    # get project name, from the directory name
    projectSetupFile = os.path.join(projectSetDir,'Setup',projectName+'Set'+str(setNum)+'Setup.xml')

    # get the time step
    timeStep = readXmlTag(projectSetupFile,'timeStep','value',returnDtype = 'int')[0]

    # get the time steps to run
    runTimeSteps = readXmlTag(projectSetupFile,'runTimeSteps','value')
    if len(runTimeSteps) == 1: # if only one value, take out of list. this prevents failures further down.
        runTimeSteps = runTimeSteps[0]
        if not runTimeSteps == 'all':
            runTimeSteps = int(runTimeSteps)
    else: # convert to int
        runTimeSteps = [int(x) for x in runTimeSteps]

    # get the load predicting function
    predictLoad = readXmlTag(projectSetupFile,'predictLoad','value')[0]

    # get the wind predicting function
    predictWind = readXmlTag(projectSetupFile,'predictWind','value')[0]

    # get the ees dispatch
    eesDispatch = readXmlTag(projectSetupFile,'eesDispatch','value')[0]

    # get the tes dispatch
    tesDispatch = readXmlTag(projectSetupFile, 'tesDispatch', 'value')[0]

    # get the minimum required SRC calculation
    getMinSrcFile = readXmlTag(projectSetupFile, 'getMinSrc', 'value')[0]

    getMinSrcInputFile = os.path.join(projectSetDir, 'Setup',
                                       projectName + 'Set' + str(setNum) + getMinSrcFile[0].upper() + getMinSrcFile[
                                                                                                       1:] + 'Inputs.xml')

    # get the components to run
    componentNames = readXmlTag(projectSetupFile, 'componentNames', 'value')

    # get the load profile to run
    loadProfileFile = readXmlTag(projectSetupFile, 'loadProfileFile', 'value')[0]
    loadProfileFile = os.path.join(timeSeriesDir,loadProfileFile)

    # get the RE dispatch
    reDispatchFile = readXmlTag(projectSetupFile, 'reDispatch', 'value')[0]

    reDispatchInputFile = os.path.join(projectSetDir, 'Setup', projectName + 'Set' + str(setNum) + reDispatchFile[0].upper() + reDispatchFile[1:] + 'Inputs.xml')

    # TODO
    # get the gen dispatch
    genDispatch = []
    # get the wtg dispatch
    wtgDispatch = []

    while 1:
        # read the SQL table of runs in this set and look for the next run that has not been started yet.
        conn = sqlite3.connect(os.path.join(projectSetDir,'set' + str(setNum) + 'ComponentAttributes.db') )# create sql database
        df = pd.read_sql_query('select * from compAttributes',conn)
        # try to find the first 0 value in started column
        try:
            runNum = list(df['started']).index(0)
        except: # there are no more simulations left to run
            break
        # set started value to 1 to indicate starting the simulations
        df.at[runNum, 'started'] = 1
        df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        conn.close()
        # Go to run directory and run
        runDir = os.path.join(projectSetDir,'Run'+ str(runNum))
        runCompDir = os.path.join(runDir,'Components') # component directory for this run
        # output data dir
        outputDataDir = os.path.join(runDir, 'OutputData')
        if not os.path.exists(outputDataDir): # if doesnt exist, create
            os.mkdir(outputDataDir)

        eesIDs = []
        eesSOC = []
        eesStates = []
        eesSRC = []
        eesDescriptors = []
        tesIDs = []
        tesT = []
        tesStates = []
        tesDescriptors = []
        wtgIDs = []
        wtgStates = []
        wtgDescriptors = []
        genIDs = []
        genStates = []
        genDescriptors = []
        loadDescriptors = []


        for cpt in componentNames:  # for each component
            # check if component is a generator
            if 'gen' in cpt.lower():
                genDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                genIDs += [cpt[3:]]
                genStates += [2]
            elif 'ees' in cpt.lower():  # or if energy storage
                eesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                eesIDs += [cpt[3:]]
                eesStates += [2]
                eesSRC += [0]
                eesSOC += [0]
            elif 'tes' in cpt.lower():  # or if energy storage
                tesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                tesIDs += [cpt[3:]]
                tesT += [295]
                tesStates += [2]
            elif 'wtg' in cpt.lower():  # or if wind turbine
                wtgDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(runNum) + 'Descriptor.xml')]
                wtgIDs += [cpt[3:]]
                wtgStates += [2]
            elif 'load' in cpt.lower():  # or if wind turbine
                loadDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Set' + str(setNum) + 'Run' + str(
                    runNum) + 'Descriptor.xml')]

        # initiate the system operations
        # code profiler
        # pr0 = cProfile.Profile()
        # pr0.enable()
        SO = SystemOperations(timeStep = timeStep, runTimeSteps = runTimeSteps, loadRealFiles = loadProfileFile, loadReactiveFiles = [],
                              predictLoad = predictLoad, loadDescriptor = loadDescriptors, predictWind = predictWind, getMinSrcFile = getMinSrcFile, getMinSrcInputFile = getMinSrcInputFile, reDispatchFile = reDispatchFile, reDispatchInputsFile = reDispatchInputFile,
                         genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatch = genDispatch,
                         wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptors, wtgSpeedFiles = timeSeriesDir, wtgDispatch = wtgDispatch,
                         eesIDs = eesIDs, eesStates = eesStates, eesSOCs = eesSOC, eesDescriptors = eesDescriptors, eesDispatch = eesDispatch,
                         tesIDs = tesIDs, tesTs = tesT, tesStates=tesStates, tesDescriptors=tesDescriptors, tesDispatch=tesDispatch)
        # stop profiler
        # pr0.disable()
        #pr0.print_stats(sort="calls")

        # run the simulation
        # code profiler
        # pr1 = cProfile.Profile()
        # pr1.enable()
        # run sim
        SO.runSimulation()
        # stop profiler
        # pr1.disable()
        # pr1.print_stats(sort="calls")

        # save data
        os.chdir(outputDataDir)
        writeNCFile(SO.DM.realTime,SO.powerhouseP,1,0,'kW','powerhousePSet' + str(setNum) + 'Run'+str(runNum)+'.nc') # gen P
        writeNCFile(SO.DM.realTime, SO.powerhousePch, 1, 0, 'kW',
                    'powerhousePchSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # gen Pch
        writeNCFile(SO.DM.realTime, SO.rePlimit, 1, 0, 'kW', 'rePlimitSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # rePlimit
        writeNCFile(SO.DM.realTime, SO.wfPAvail, 1, 0, 'kW', 'wtgPAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wfPAvail
        writeNCFile(SO.DM.realTime, SO.wfPImport, 1, 0, 'kW', 'wtgPImportSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wtgPImport
        writeNCFile(SO.DM.realTime, SO.wfPch, 1, 0, 'kW', 'wtgPchSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wtgPch
        writeNCFile(SO.DM.realTime, SO.wfPTot, 1, 0, 'kW', 'wtgPTotSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wtgPTot
        writeNCFile(SO.DM.realTime, SO.srcMin, 1, 0, 'kW', 'srcMinSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # srcMin
        writeNCFile(SO.DM.realTime, SO.eessDis, 1, 0, 'kW', 'eessDisSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # eesDis
        writeNCFile(SO.DM.realTime, SO.eessP, 1, 0, 'kW', 'eessPSet' + str(setNum) + 'Run' + str(runNum) + '.nc')
        writeNCFile(SO.DM.realTime, SO.tesP, 1, 0, 'kW', 'tessP' + str(setNum) + 'Run' + str(runNum) + '.nc') # tessP
        writeNCFile(SO.DM.realTime, SO.genPAvail, 1, 0, 'kW', 'genPAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # genPAvail
        writeNCFile(SO.DM.realTime, SO.onlineCombinationID, 1, 0, 'NA', 'onlineCombinationIDSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # onlineCombinationID
        writeNCFile(SO.DM.realTime, SO.underSRC, 1, 0, 'kW', 'underSRCSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # underSRC
        writeNCFile(SO.DM.realTime, SO.outOfNormalBounds, 1, 0, 'bool', 'outOfNormalBoundsSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # outOfNormalBounds
        writeNCFile(SO.DM.realTime, SO.wfSpilledWindFlag, 1, 0, 'bool',
                    'wfSpilledWindFlagSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wfSpilledWindFlag
        writeNCFile(SO.DM.realTime, SO.futureLoadList, 1, 0, 'kW',
                    'futureLoad' + str(setNum) + 'Run' + str(runNum) + '.nc')  # future Load predicted
        writeNCFile(SO.DM.realTime, SO.futureSRC, 1, 0, 'kW',
                    'futureSRC' + str(setNum) + 'Run' + str(runNum) + '.nc')  # future SRC predicted

        # power each generators
        for idx, genP in enumerate(zip(*SO.genP)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genP, 1, 0, 's',
                        'gen' + str(SO.PH.genIDS[idx]) + 'PSet' + str(setNum) + 'Run' + str(
                            runNum) + '.nc')

        # start times for each generators
        for idx, genST in enumerate(zip(*SO.genStartTime)): # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genST, 1, 0, 's', 'gen' + str(SO.PH.genIDS[idx]) + 'StartTimeSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # eessSoc

        # run times for each generators
        for idx, genRT in enumerate(zip(*SO.genRunTime)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genRT, 1, 0, 's',
                        'gen' + str(SO.PH.genIDS[idx]) + 'RunTimeSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  #

        # SRC for each ees
        for idx, eesSRC in enumerate(zip(*SO.eessSrc)):  # for each eess
            writeNCFile(SO.DM.realTime, eesSRC, 1, 0, 'kW',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'SRCSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  #

        # SOC for each ees
        for idx, eesSOC in enumerate(zip(*SO.eessSoc)):  # for each eess
            writeNCFile(SO.DM.realTime, eesSOC, 1, 0, 'PU',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'SOCSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # eessSoc

        # ees loss
        for idx, eesLoss in enumerate(zip(*SO.eesPLoss)):  # for each eess
            writeNCFile(SO.DM.realTime, eesLoss, 1, 0, 'kW',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'LossSet' + str(setNum) + 'Run' + str(runNum) + '.nc')

        # wtg P avail
        for idx, wtgPAvail in enumerate(zip(*SO.wtgPAvail)):  # for wtg
            writeNCFile(SO.DM.realTime, wtgPAvail, 1, 0, 'kW',
                        'wtg' + str(SO.WF.wtgIDS[idx]) + 'PAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc')

        # wtg P
        for idx, wtgP in enumerate(zip(*SO.wtgP)):  # for each wtg
            writeNCFile(SO.DM.realTime, wtgP, 1, 0, 'kW',
                        'wtg' + str(SO.WF.wtgIDS[idx]) + 'PSet' + str(setNum) + 'Run' + str(runNum) + '.nc')

        # future wind predicted
        for idx, fw in enumerate(zip(*SO.futureWindList)):  # for each wtg
            writeNCFile(SO.DM.realTime, fw, 1, 0, 'kW',
                        'wtg' + str(SO.WF.wtgIDS[idx]) + 'FutureWind' + str(setNum) + 'Run' + str(runNum) + '.nc')

        # set the value in the 'finished' for this run to 1 to indicate it is finished.
        conn = sqlite3.connect(
            os.path.join(projectSetDir, 'set' + str(setNum) + 'ComponentAttributes.db'))  # create sql database
        df = pd.read_sql_query('select * from compAttributes', conn)
        # set finished value to 1 to indicate this run is finshed
        df['finished'][runNum] = 1
        df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        conn.close()