# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 28, 2018
# License: MIT License (see LICENSE file of this package for more information)

import cProfile
import numpy as np
import numpy as np
import os
import os
import pandas as pd
# add to sys path
import sys
import tkinter as tk
from shutil import copyfile
from tkinter import filedialog

from SystemOperations import SystemOperations

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
sys.path.append(here)
from GBSInputHandler.writeXmlTag import writeXmlTag
from GBSInputHandler.readXmlTag import readXmlTag
from GBSInputHandler.fillProjectData import fillProjectData
import glob
from GBSAnalyzer.DataWriters.writeNCFile import writeNCFile
from GBSInputHandler.writeXmlTag import writeXmlTag

def runSimulation(projectDir = '', runTimeSteps = 'all'):

    if projectDir == '':
        print('Choose the project directory')
        root = tk.Tk()
        root.withdraw()
        projectDir = filedialog.askdirectory()

    # create and fill project files
    fillProjectData(projectDir)

    # get project name, from the directory name
    projectName = os.path.basename(projectDir)
    projectSetupFile = os.path.join(projectDir,'InputData','Setup',projectName+'Setup.xml')
    userInputDir = projectDir + '/InputData/Setup/UserInput/'
    componentDir = projectDir + '/InputData/Components/'
    timeSeriesDir = projectDir + '/InputData/TimeSeriesData/ProcessedData/'
    outputDataDir = projectDir + '/OutputData/'

    # get the time step
    timeStep = readXmlTag(projectSetupFile,'timeStep','value',returnDtype = 'int')[0]

    # get the load predicting function
    predictLoad = readXmlTag(projectSetupFile,'predictLoad','value')[0]

    # get the wind predicting function
    predictWind = readXmlTag(projectSetupFile,'predictWind','value')[0]

    # get the ees dispatch
    eesDispatch = readXmlTag(projectSetupFile,'eesDispatch','value')[0]

    # get the minimum required SRC calculation
    getMinSrcFile = readXmlTag(projectSetupFile, 'getMinSrc', 'value')[0]

    # TODO
    # get the gen dispatch
    genDispatch = []
    # get the wtg dispatch
    wtgDispatch = []

    # get the components to run in each simulation
    simComponentsFile = os.path.join(userInputDir,'simulationComponents.csv')
    componentsDF = pd.read_csv(simComponentsFile)  # read as a data frame
    componentsDF = componentsDF.fillna('')  # remplace nan values with empty
    componentsMX = componentsDF.as_matrix() # save matrix version

    '''
    # get the real load files
    os.chdir(timeSeriesDir)
    # check if there is a load file
    if os.path.exists('load.nc'):
        loadRealFiles = [os.path.join(timeSeriesDir,'load.nc')]
    else:
        # if there is no load file, need to add up all generation
        loadRealFiles = []
        for file in
          glob.glob('P.nc'):
            loadRealFiles += [os.path.join(timeSeriesDir,file)]
    '''
    for run in range(componentsMX.shape[1]): # for each column, each simulation run
        # check if there already is a directory for this run number. If there is, then it has already been run, skip it.
        if not os.path.isdir(os.path.join(outputDataDir,'Run'+str(run))):
            components = componentsMX[:,run]
            components = [x for x in components if not x == '']

            eesIDs = []
            eesSOC = []
            eesStates = []
            eesSRC = []
            eesDescriptors = []
            wtgIDs = []
            wtgStates = []
            wtgDescriptors = []
            windSpeed = []
            genIDs = []
            genStates = []
            genDescriptors = []
            loadRealFiles = []
            for cpt in components: # for each component
                # check if component is a generator
                if 'gen' in cpt.lower():
                    genDescriptors += [os.path.join(componentDir,cpt.lower()+'Descriptor.xml')]
                    genIDs += [cpt[3:]]
                    genStates += [2]
                elif 'ees' in cpt.lower(): # or if energy storage
                    eesDescriptors += [os.path.join(componentDir, cpt.lower() + 'Descriptor.xml')]
                    eesIDs += [cpt[3:]]
                    eesStates += [2]
                    eesSRC += [0]
                    eesSOC += [0]
                elif 'wtg' in cpt.lower(): # or if wind turbine
                    wtgDescriptors += [os.path.join(componentDir, cpt.lower() + 'Descriptor.xml')]
                    wtgIDs += [cpt[3:]]
                    wtgStates += [2]
                    windSpeed += [os.path.join(timeSeriesDir, cpt.lower() + 'WS.nc')]
                elif 'load' in cpt.lower(): # if the load profile
                    loadRealFiles = os.path.join(timeSeriesDir, cpt.lower() + '.nc')





            # initiate the system operations
            # code profiler
            pr0 = cProfile.Profile()
            pr0.enable()
            SO = SystemOperations(timeStep = timeStep, runTimeSteps = runTimeSteps, loadRealFiles = loadRealFiles, loadReactiveFiles = [],
                                  predictLoad = predictLoad, predictWind = predictWind, getMinSrcFile = getMinSrcFile,
                             genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatch = genDispatch,
                             wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptors, wtgSpeedFiles = windSpeed, wtgDispatch = wtgDispatch,
                             eesIDs = eesIDs, eesStates = eesStates, eesSOCs = eesSOC, eesDescriptors = eesDescriptors, eesDispatch = eesDispatch)
            # stop profiler
            pr0.disable()
            pr0.print_stats(sort="calls")

            # run the simulation
            # code profiler
            pr1 = cProfile.Profile()
            pr1.enable()
            # run sim
            SO.runSimulation()
            # stop profiler
            pr1.disable()
            pr1.print_stats(sort="calls")

            # save data
            os.chdir(outputDataDir)
            os.mkdir('Run'+str(run))
            os.chdir('Run'+str(run))
            writeNCFile(SO.DM.realTime,SO.genP,1,0,'kW','genPRun'+str(run)+'.nc') # gen P
            writeNCFile(SO.DM.realTime, SO.rePlimit, 1, 0, 'kW', 'rePlimitRun' + str(run) + '.nc')  # rePlimit
            writeNCFile(SO.DM.realTime, SO.wtgPAvail, 1, 0, 'kW', 'wtgPAvailRun' + str(run) + '.nc')  # wtgPAvail
            writeNCFile(SO.DM.realTime, SO.wtgPImport, 1, 0, 'kW', 'wtgPImportRun' + str(run) + '.nc')  # wtgPImport
            writeNCFile(SO.DM.realTime, SO.wtgPch, 1, 0, 'kW', 'wtgPchRun' + str(run) + '.nc')  # wtgPch
            writeNCFile(SO.DM.realTime, SO.wtgPTot, 1, 0, 'kW', 'wtgPTotRun' + str(run) + '.nc')  # wtgPTot
            writeNCFile(SO.DM.realTime, SO.srcMin, 1, 0, 'kW', 'srcMinRun' + str(run) + '.nc')  # srcMin
            writeNCFile(SO.DM.realTime, SO.eesDis, 1, 0, 'kW', 'eesDisRun' + str(run) + '.nc')  # eesDis
            writeNCFile(SO.DM.realTime, SO.genPAvail, 1, 0, 'kW', 'genPAvailRun' + str(run) + '.nc')  # genPAvail
            writeNCFile(SO.DM.realTime, SO.onlineCombinationID, 1, 0, 'NA', 'onlineCombinationIDRun' + str(run) + '.nc')  # onlineCombinationID
            writeNCFile(SO.DM.realTime, SO.underSRC, 1, 0, 'kW', 'underSRCRun' + str(run) + '.nc')  # underSRC
            writeNCFile(SO.DM.realTime, SO.outOfNormalBounds, 1, 0, 'kW', 'outOfNormalBoundsRun' + str(run) + '.nc')  # outOfNormalBounds

            # start times for each generators
            for idx, genST in enumerate(zip(*SO.genStartTime)): # for each generator in the powerhouse
                writeNCFile(SO.DM.realTime, genST, 1, 0, 's', 'gen' + str(SO.PH.genIDS[idx]) + 'StartTimeRun' + str(run) + '.nc')  # eessSoc

            # run times for each generators
            for idx, genRT in enumerate(zip(*SO.genRunTime)):  # for each generator in the powerhouse
                writeNCFile(SO.DM.realTime, genRT, 1, 0, 's',
                            'gen' + str(SO.PH.genIDS[idx]) + 'RunTimeRun' + str(run) + '.nc')  #

            # SRC for each ees
            for idx, eesSRC in enumerate(zip(*SO.eessSrc)):  # for each generator in the powerhouse
                writeNCFile(SO.DM.realTime, eesSRC, 1, 0, 'kW',
                            'ees' + str(SO.EESS.eesIDs[idx]) + 'SRCRun' + str(run) + '.nc')  #

            # SOC for each ees
            for idx, eesSOC in enumerate(zip(*SO.eessSoc)):  # for each generator in the powerhouse
                writeNCFile(SO.DM.realTime, eesSOC, 1, 0, 'PU',
                            'ees' + str(SO.EESS.eesIDs[idx]) + 'SOCRun' + str(run) + '.nc')  # eessSoc

            # copy project setup file to the run directory
            copyfile(projectSetupFile, projectName+'Setup.xml')

            # copy the component used file to the run directory
            componentsUsedFile = os.path.join(here, 'Resources', 'Setup', 'projectRunComponentsUsed.xml')
            saveComponentsName = projectName + 'Run' + str(run) + 'ComonentsUsed.xml'
            copyfile(componentsUsedFile, saveComponentsName)
            # write project name
            writeXmlTag(saveComponentsName, 'project', 'name', projectName)
            # write run number
            writeXmlTag(saveComponentsName, 'runNumber', 'value', run)
            # list of components
            writeXmlTag(saveComponentsName, 'components', 'value', components)

    print('done')
