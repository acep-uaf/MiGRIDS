# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 28, 2018
# License: MIT License (see LICENSE file of this package for more information)

import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here,".."))
import sqlite3
import time
# add to sys path

import tkinter as tk
from tkinter import filedialog

import pandas as pd

from Model.Operational.SystemOperations import SystemOperations

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
sys.path.append(here)
from Analyzer.DataRetrievers.readXmlTag import readXmlTag
from Analyzer.DataWriters.writeNCFile import writeNCFile


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
    predictLoadFile = readXmlTag(projectSetupFile,'predictLoad','value')[0]
    predictLoadInputsFile = os.path.join(projectSetDir, 'Setup',
                                        projectName + 'Set' + str(setNum) + predictLoadFile[
                                            0].upper() + predictLoadFile[
                                                         1:] + 'Inputs.xml')

    # get the wind predicting function
    predictWindFile = readXmlTag(projectSetupFile,'predictWind','value')[0]
    predictWindInputsFile = os.path.join(projectSetDir, 'Setup',
                                         projectName + 'Set' + str(setNum) + predictWindFile[
                                             0].upper() + predictWindFile[
                                                          1:] + 'Inputs.xml')

    # get the ees dispatch
    eesDispatchFile = readXmlTag(projectSetupFile,'eesDispatch','value')[0]
    eesDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                        projectName + 'Set' + str(setNum) + eesDispatchFile[
                                            0].upper() + eesDispatchFile[
                                                         1:] + 'Inputs.xml')

    # get the tes dispatch
    tesDispatchFile = readXmlTag(projectSetupFile, 'tesDispatch', 'value')[0]
    tesDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                        projectName + 'Set' + str(setNum) + tesDispatchFile[
                                            0].upper() + tesDispatchFile[
                                                         1:] + 'Inputs.xml')

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

    # get the gen dispatch
    genDispatchFile = readXmlTag(projectSetupFile, 'genDispatch', 'value')[0]

    genDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                       projectName + 'Set' + str(setNum) + genDispatchFile[0].upper() + genDispatchFile[
                                                                                                       1:] + 'Inputs.xml')
    # get the gen schedule
    genScheduleFile = readXmlTag(projectSetupFile, 'genSchedule', 'value')[0]

    genScheduleInputFile = os.path.join(projectSetDir, 'Setup',
                                        projectName + 'Set' + str(setNum) + genScheduleFile[
                                            0].upper() + genScheduleFile[
                                                         1:] + 'Inputs.xml')

    # get the wtg dispatch
    wtgDispatchFile = readXmlTag(projectSetupFile, 'wtgDispatch', 'value')[0]

    wtgDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                        projectName + 'Set' + str(setNum) + wtgDispatchFile[
                                            0].upper() + wtgDispatchFile[
                                                         1:] + 'Inputs.xml')

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
        SO = SystemOperations(outputDataDir, timeStep = timeStep, runTimeSteps = runTimeSteps, loadRealFiles = loadProfileFile, loadReactiveFiles = [],
                              predictLoadFile = predictLoadFile, predictLoadInputsFile=predictLoadInputsFile,
                              loadDescriptor = loadDescriptors, predictWindFile = predictWindFile, predictWindInputsFile=predictWindInputsFile,
                              getMinSrcFile = getMinSrcFile, getMinSrcInputFile = getMinSrcInputFile, reDispatchFile = reDispatchFile, reDispatchInputsFile = reDispatchInputFile,
                         genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatchFile = genDispatchFile,
                            genScheduleFile = genScheduleFile, genDispatchInputsFile= genDispatchInputFile, genScheduleInputsFile= genScheduleInputFile,
                         wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptors, windSpeedDir = timeSeriesDir,
                            wtgDispatchFile=wtgDispatchFile, wtgDispatchInputsFile=wtgDispatchInputFile,
                         eesIDs = eesIDs, eesStates = eesStates, eesSOCs = eesSOC, eesDescriptors = eesDescriptors, eesDispatchFile = eesDispatchFile, eesDispatchInputsFile= eesDispatchInputFile,
                         tesIDs = tesIDs, tesTs = tesT, tesStates=tesStates, tesDescriptors=tesDescriptors, tesDispatchFile=tesDispatchFile, tesDispatchInputsFile = tesDispatchInputFile )
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

        start_file_write = time.time()

        # Stitch powerhouseP
        powerhouseP = SO.stitchVariable('powerhouseP')
        writeNCFile(SO.DM.realTime, powerhouseP,1,0,'kW','powerhousePSet' + str(setNum) + 'Run'+str(runNum)+'.nc') # gen P
        powerhouseP = None

        # Stitch powerhousePch
        powerhousePch = SO.stitchVariable('powerhousePch')
        writeNCFile(SO.DM.realTime, powerhousePch, 1, 0, 'kW',
                    'powerhousePchSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # gen Pch
        powerhousePch = None

        # Stitch rePlimit
        rePlimit = SO.stitchVariable('rePlimit')
        writeNCFile(SO.DM.realTime, rePlimit, 1, 0, 'kW', 'rePlimitSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # rePlimit
        rePlimit = None

        # Stitch wfPAvail
        wfPAvail = SO.stitchVariable('wfPAvail')
        writeNCFile(SO.DM.realTime, wfPAvail, 1, 0, 'kW', 'wtgPAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wfPAvail
        wfPAvail = None

        # Stitch wfPImport
        wfPImport = SO.stitchVariable('wfPImport')
        writeNCFile(SO.DM.realTime, wfPImport, 1, 0, 'kW', 'wtgPImportSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wtgPImport
        wfPImport = None

        # Stitch wfPch
        wfPch = SO.stitchVariable('wfPch')
        writeNCFile(SO.DM.realTime, wfPch, 1, 0, 'kW', 'wtgPchSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wtgPch
        wfPch = None

        # Stitch wfPTot
        wfPTot = SO.stitchVariable('wfPTot')
        writeNCFile(SO.DM.realTime, wfPTot, 1, 0, 'kW', 'wtgPTotSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wtgPTot
        wfPTot = None

        # Stitch srcMin
        srcMin = SO.stitchVariable('srcMin')
        writeNCFile(SO.DM.realTime, srcMin, 1, 0, 'kW', 'srcMinSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # srcMin
        srcMin = None

        # Stitch eessDis and write to disk
        eessDis = SO.stitchVariable('eessDis')
        writeNCFile(SO.DM.realTime, eessDis, 1, 0, 'kW', 'eessDisSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # eesDis
        eessDis = None

        # Stitch eessP  and write to disk
        eessP = SO.stitchVariable('eessP')
        writeNCFile(SO.DM.realTime, eessP, 1, 0, 'kW', 'eessPSet' + str(setNum) + 'Run' + str(runNum) + '.nc')
        eessP = None

        # Stitch tesP and write to disk
        tesP = SO.stitchVariable('tesP')
        writeNCFile(SO.DM.realTime, tesP, 1, 0, 'kW', 'tessP' + str(setNum) + 'Run' + str(runNum) + '.nc') # tessP
        tesP = None

        # Stitch genPAvail and write to disk
        genPAvail = SO.stitchVariable('genPAvail')
        writeNCFile(SO.DM.realTime, genPAvail, 1, 0, 'kW', 'genPAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # genPAvail
        genPAvail = None

        # Stitch onlineCombinationID and write to disk
        onlineCombinationID = SO.stitchVariable('onlineCombinationID')
        writeNCFile(SO.DM.realTime, onlineCombinationID, 1, 0, 'NA', 'onlineCombinationIDSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # onlineCombinationID
        onlineCombinationID = None

        # Stitch underSRC and write to disk
        underSRC = SO.stitchVariable('underSRC')
        writeNCFile(SO.DM.realTime, underSRC, 1, 0, 'kW', 'underSRCSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # underSRC
        underSRC = None

        # Stitch outOfNormalBounds and write to disk
        outOfNormalBounds = SO.stitchVariable('outOfNormalBounds')
        writeNCFile(SO.DM.realTime, outOfNormalBounds, 1, 0, 'bool', 'outOfNormalBoundsSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # outOfNormalBounds
        outOfNormalBounds = None

        # Stitch outOfEfficientBounds and write to disk
        outOfEfficientBounds = SO.stitchVariable('outOfEfficientBounds')
        writeNCFile(SO.DM.realTime, outOfEfficientBounds, 1, 0, 'bool',
                    'outOfEfficientBoundsSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # outOfEfficientBounds
        outOfEfficientBounds = None

        # Stitch wfSpilledWindFlag and write to disk
        wfSpilledWindFlag = SO.stitchVariable('wfSpilledWindFlag')
        writeNCFile(SO.DM.realTime, wfSpilledWindFlag, 1, 0, 'bool',
                    'wfSpilledWindFlagSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # wfSpilledWindFlag

        # Stitch futureLoadList and write to disk
        futureLoadList = SO.stitchVariable('futureLoadList')
        writeNCFile(SO.DM.realTime, futureLoadList, 1, 0, 'kW',
                    'futureLoad' + str(setNum) + 'Run' + str(runNum) + '.nc')  # future Load predicted
        futureLoadList = None

        # Stitch futureSRC and write to disk
        futureSRC = SO.stitchVariable('futureSRC')
        writeNCFile(SO.DM.realTime, futureSRC, 1, 0, 'kW',
                    'futureSRC' + str(setNum) + 'Run' + str(runNum) + '.nc')  # future SRC predicted
        futureSRC = None

        # power each generators
        genP = SO.stitchVariable('genP')
        for idx, genP in enumerate(zip(*genP)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genP, 1, 0, 's',
                        'gen' + str(SO.PH.genIDS[idx]) + 'PSet' + str(setNum) + 'Run' + str(
                            runNum) + '.nc')
        genP = None

        # start times for each generators
        genStartTime = SO.stitchVariable('genStartTime')
        for idx, genST in enumerate(zip(*genStartTime)): # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genST, 1, 0, 's', 'gen' + str(SO.PH.genIDS[idx]) + 'StartTimeSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # eessSoc
        genStartTime = None

        # run times for each generators
        genRunTime = SO.stitchVariable('genRunTime')
        for idx, genRT in enumerate(zip(*genRunTime)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genRT, 1, 0, 's',
                        'gen' + str(SO.PH.genIDS[idx]) + 'RunTimeSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  #
        genRunTime = None

        # SRC for each ees
        eessSrc = SO.stitchVariable('eessSrc')
        for idx, eesSRC in enumerate(zip(*eessSrc)):  # for each eess
            writeNCFile(SO.DM.realTime, eesSRC, 1, 0, 'kW',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'SRCSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  #
        eessSrc = None

        # SOC for each ees
        eessSoc = SO.stitchVariable('eessSoc')
        for idx, eesSOC in enumerate(zip(*eessSoc)):  # for each eess
            writeNCFile(SO.DM.realTime, eesSOC, 1, 0, 'PU',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'SOCSet' + str(setNum) + 'Run' + str(runNum) + '.nc')  # eessSoc
        eessSoc = None

        # ees loss
        eesPLoss = SO.stitchVariable('eesPLoss')
        for idx, eesLoss in enumerate(zip(*eesPLoss)):  # for each eess
            writeNCFile(SO.DM.realTime, eesLoss, 1, 0, 'kW',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'LossSet' + str(setNum) + 'Run' + str(runNum) + '.nc')
        eesPLoss = None

        # wtg P avail
        wtgPAvail = SO.stitchVariable('wtgPAvail')
        for idx, wtgPAvail in enumerate(zip(*wtgPAvail)):  # for wtg
            writeNCFile(SO.DM.realTime, wtgPAvail, 1, 0, 'kW',
                        'wtg' + str(SO.WF.wtgIDS[idx]) + 'PAvailSet' + str(setNum) + 'Run' + str(runNum) + '.nc')
        wtgPAvail = None

        # wtg P
        wtgP = SO.stitchVariable('wtgP')
        for idx, wtgP in enumerate(zip(*wtgP)):  # for each wtg
            writeNCFile(SO.DM.realTime, wtgP, 1, 0, 'kW',
                        'wtg' + str(SO.WF.wtgIDS[idx]) + 'PSet' + str(setNum) + 'Run' + str(runNum) + '.nc')
        wtgP = None

        # future wind predicted
        futureWindList = SO.stitchVariable('futureWindList')
        for idx, fw in enumerate(zip(*futureWindList)):  # for each wtg
            writeNCFile(SO.DM.realTime, fw, 1, 0, 'kW',
                        'wtg' + str(SO.WF.wtgIDS[idx]) + 'FutureWind' + str(setNum) + 'Run' + str(runNum) + '.nc')
        futureWindList = None

        print('File write operation elapsed time: ' + str(time.time() - start_file_write))

        # set the value in the 'finished' for this run to 1 to indicate it is finished.
        conn = sqlite3.connect(
            os.path.join(projectSetDir, 'set' + str(setNum) + 'ComponentAttributes.db'))  # create sql database
        df = pd.read_sql_query('select * from compAttributes', conn)
        # set finished value to 1 to indicate this run is finshed
        df['finished'][runNum] = 1
        df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        conn.close()