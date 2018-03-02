
import os
import numpy as np
from SystemOperations import SystemOperations
import cProfile

# Time step

timeStep = 1

# Energy Storage

eesIDS = [0,1]
eesSOC = [0.5]*2
eesStates = [2]*2
eesSRC = [100]*2
eesDescriptor = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\Components\ees0Descriptor.xml']\
                + ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\Components\ees1Descriptor.xml']
eesDispatch = 'eesDispatch1'

# Wind Turbines

wtgIDs = list(range(12))
wtgStates = [2]*12
timeStep = 1
wtgDescriptor = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\wtg1Descriptor.xml']*12
windSpeed = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg1WS.nc'

# Generators

genIDs = [0,1,2]
genStates = [2,0,0]
genDescriptors = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen1Descriptor.xml',
                  'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen2Descriptor.xml',
                  'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen3Descriptor.xml']

 # Demand

loadRealFiles = [
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\gen1P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\gen2P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\gen3P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg1P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg2P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg3P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg4P.nc']

# Predict Load

predictLoad = 'predictLoad1'
# code profiler
pr0 = cProfile.Profile()
pr0.enable()
SO = SystemOperations(timeStep = timeStep, loadRealFiles = loadRealFiles, loadReactiveFiles = [], predictLoad = predictLoad,
                 genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatch = [],
                 wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptor, wtgSpeedFiles = windSpeed,
                 eesIDs = eesIDS, eesStates = eesStates, eesSOCs = eesSOC, eesDescriptors = eesDescriptor, eesDispatch = eesDispatch)
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