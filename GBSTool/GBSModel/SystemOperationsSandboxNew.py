
import cProfile
import os
import sys
import tkinter as tk
from tkinter import filedialog

import numpy as np
import pandas as pd
from SystemOperations import SystemOperations

sys.path.append('../')
from GBSAnalyzer.DataRetrievers.readXmlTag import readXmlTag
import glob
from GBSAnalyzer.DataWriters import writeNCFile

print('Choose the project directory')
root = tk.Tk()
root.withdraw()
projectDir = filedialog.askdirectory()

# get project name, from the directory name
projectName = os.path.basename(projectDir)
projectSetupFile = os.path.join(projectDir,'InputData','Setup',projectName+'Setup.xml')
userInputDir = projectDir + '/InputData/Setup/UserInput/'
componentDir = projectDir + '/InputData/Components/'
timeSeriesDir = projectDir + '/InputData/TimeSeriesData/ProcessedData/'
outputDataDir = projectDir + '/OutputData'

# get the time step
timeStep = readXmlTag(projectSetupFile,'timeStep','value',returnDtype = 'int')[0]

# get the load predicting function
predictLoad = readXmlTag(projectSetupFile,'predictLoad','value')[0]

# get the wind predicting function
predictWind = readXmlTag(projectSetupFile,'predictWind','value')[0]

# get the ees dispatch
eesDispatch = readXmlTag(projectSetupFile,'eesDispatch','value')[0]

# get the components to run in each simulation
simComponentsFile = os.path.join(userInputDir,'simulationComponents.csv')
componentsDF = pd.read_csv(simComponentsFile)  # read as a data frame
componentsDF = componentsDF.fillna('')  # remplace nan values with empty
componentsMX = componentsDF.as_matrix() # save matrix version

# get the real load files
os.chdir(timeSeriesDir)
# check if there is a load file
if os.path.exists('load.nc'):
    loadRealFiles = [os.path.join(timeSeriesDir,'load.nc')]
else:
    # if there is no load file, need to add up all generation
    loadRealFiles = []
    for file in  glob.glob('P.nc'):
        loadRealFiles += [os.path.join(timeSeriesDir,file)]

for run in range(componentsMX.shape[0]): # for each column, each simulation run
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




    # initiate the system operations
    # code profiler
    pr0 = cProfile.Profile()
    pr0.enable()
    SO = SystemOperations(timeStep = timeStep, loadRealFiles = loadRealFiles, loadReactiveFiles = [], predictLoad = predictLoad, predictWind = predictWind,
                     genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatch = [],
                     wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptors, wtgSpeedFiles = windSpeed,
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
    writeNCFile(SO.DM.realTime, SO.genP, 1, 0, 'kW', 'genPRun' + str(run) + '.nc') # gen P
    writeNCFile(SO.DM.realTime, SO.rePlimit, 1, 0, 'kW', 'rePlimit' + str(run) + '.nc')  # rePlimit
    writeNCFile(SO.DM.realTime, SO.wtgPAvail, 1, 0, 'kW', 'wtgPAvail' + str(run) + '.nc')  # wtgPAvail
    writeNCFile(SO.DM.realTime, SO.wtgPImport, 1, 0, 'kW', 'wtgPImport' + str(run) + '.nc')  # wtgPImport
    writeNCFile(SO.DM.realTime, SO.wtgPch, 1, 0, 'kW', 'wtgPch' + str(run) + '.nc')  # wtgPch
    writeNCFile(SO.DM.realTime, SO.wtgPTot, 1, 0, 'kW', 'wtgPTot' + str(run) + '.nc')  # wtgPTot
    writeNCFile(SO.DM.realTime, SO.srcMin, 1, 0, 'kW', 'srcMin' + str(run) + '.nc')  # srcMin
    writeNCFile(SO.DM.realTime, SO.eesDis, 1, 0, 'kW', 'eesDis' + str(run) + '.nc')  # eesDis
    writeNCFile(SO.DM.realTime, SO.genPAvail, 1, 0, 'kW', 'genPAvail' + str(run) + '.nc')  # genPAvail
    writeNCFile(SO.DM.realTime, SO.eessSrc, 1, 0, 'kW', 'eessSrc' + str(run) + '.nc')  # eessSrc
    writeNCFile(SO.DM.realTime, SO.eessSoc, 1, 0, 'kW', 'eessSoc' + str(run) + '.nc')  # eessSoc
    writeNCFile(SO.DM.realTime, SO.onlineCombinationID, 1, 0, 'NA', 'onlineCombinationID' + str(run) + '.nc')  # onlineCombinationID
    writeNCFile(SO.DM.realTime, SO.underSRC, 1, 0, 'kW', 'underSRCRun' + str(run) + '.nc')  # underSRC
    writeNCFile(SO.DM.realTime, SO.outOfNormalBounds, 1, 0, 'kW', 'outOfNormalBoundsRun' + str(run) + '.nc')  # outOfNormalBounds

    # start times for each generators
    for idx, genST in enumerate(zip(*SO.genStartTime)): # for each generator in the powerhouse
        writeNCFile(SO.DM.realTime, genST, 1, 0, 's', 'gen' + str(SO.PH.genIDS[idx]) + 'StartTimeRun' + str(run) + '.nc')  # eessSoc

    # run times for each generators
    for idx, genRT in enumerate(zip(*SO.genRunTime)):  # for each generator in the powerhouse
        writeNCFile(SO.DM.realTime, genRT, 1, 0, 's',
                    'gen' + str(SO.PH.genIDS[idx]) + 'RunTimeRun' + str(run) + '.nc')  # eessSoc

print('done')

import matplotlib.pyplot as plt
plt.figure()
plt.plot(np.array(SO.DM.realLoad[:100000]))
plt.plot(SO.genP) # gen output
plt.plot(SO.genPAvail)
plt.plot(SO.wtgPImport) # wtg import
plt.plot(SO.rePlimit)
plt.plot(SO.wtgPAvail)
plt.plot(SO.wtgPch) # wtg charging of eess
plt.plot(SO.eesDis)

# over gen operation
genDiff = np.array(SO.genP) - np.array(SO.genPAvail)
genDiff[genDiff < 0 ] = 0

plt.plot(SO.genPAvail)

plt.figure()
plt.plot(SO.eessSrc)
plt.plot(SO.eessSoc)

plt.figure()
plt.plot(np.array(SO.genP) + np.array(SO.wtgPImport) + np.array(SO.eesDis))
plt.plot(SO.DM.realLoad[:100000])
plt.plot(np.array(SO.DM.realLoad[:100000]) - (np.array(SO.genP) + np.array(SO.wtgPImport) + np.array(SO.eesDis)))

plt.figure()
plt.plot(SO.outOfNormalBounds)
plt.plot(SO.underSRC)