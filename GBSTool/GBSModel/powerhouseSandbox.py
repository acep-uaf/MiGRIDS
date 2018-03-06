import os
import numpy as np
from Powerhouse import Powerhouse
genIDs = [0,1,2]
genP = [0]*3
genQ = [0]*3
genStates = [2,2,0]
timeStep = 1
genDescriptors = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen1Descriptor.xml',
                  'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen2Descriptor.xml',
                  'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen3Descriptor.xml']
PH1 = Powerhouse(genIDs, genP, genQ, genStates, timeStep, genDescriptors)

# load test Load time series
here = os.getcwd()
os.chdir('C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\TimeSeries\ProcessedData')

from netCDF4 import Dataset
dataset = Dataset('testLoad.nc')
time = dataset.variables['time'][0]
value = dataset.variables['value'][0]

# require SRC
SRC = 100
# initiate variables
genP = []
genP1 = []
genWarmUpTime = []
genRunTime = []
#for i in range(len(value)):
for i in range(1000):
    PH1.genDispatch(value[i],0) # dispatch the generators
    PH1src = np.sum(PH1.genPAvail) - np.sum(PH1.genP) # the SRC available from power house
    # keep track of generator power
    genP.append(PH1.genP[:])
    warmUpTime = []
    runTime = []
    P = []
    for gen in PH1.generators:
        warmUpTime.append(gen.genStartTimeAct)
        runTime.append(gen.genRunTimeAct)
        P.append(gen.genP)
    genWarmUpTime.append(warmUpTime)
    genRunTime.append(runTime)
    genP1.append(P)
    # if out of bounds operation, or not enough SRC supplied
    if any(PH1.outOfNormalBounds) | (PH1src < SRC):
        PH1.genSchedule(np.mean([value[-3600:]]),SRC)

for i in range(40):
    PH1.genDispatch(600, 0)  # dispatch the generators
    if any(PH1.outOfNormalBounds) | (PH1src < SRC):
        PH1.genSchedule(600, SRC)

# save data
os.chdir('C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\OutputData')

def saveNC(time,value,ncName,units,scale,offset):
    rootgrp = Dataset(ncName, 'w', format='NETCDF4')  # create netCDF object
    rootgrp.createDimension('time', None)  # create dimension for all called time
    # create the time variable
    rootgrp.createVariable('time', 'float32', 'time')  # create a var
    rootgrp.variables['time'][:] = time  # fill with values
    # create the value variable
    rootgrp.createVariable('value', 'float32', 'time')  # create a var using the varnames
    rootgrp.variables['value'][:] = value  # fill with values
    # assign attributes
    rootgrp.variables['time'].Units = 'Unix time'  # set unit attribute
    rootgrp.variables['value'].Units = units  # set unit attribute
    rootgrp.variables['value'].Scale = scale  # set unit attribute
    rootgrp.variables['value'].Offset = offset  # set unit attribute
    # close file
    rootgrp.close()

saveNC(time,np.array(genP)[:,0],'gen0P.nc','kW','1','0')
saveNC(time,np.array(genP)[:,1],'gen1P.nc','kW','1','0')
saveNC(time,np.array(genP)[:,2],'gen2P.nc','kW','1','0')

saveNC(time,np.array(genWarmUpTime)[:,0],'gen0WarmupTime.nc','s','1','0')
saveNC(time,np.array(genWarmUpTime)[:,1],'gen1WarmupTime.nc','s','1','0')
saveNC(time,np.array(genWarmUpTime)[:,2],'gen2WarmupTime.nc','s','1','0')

# plot results
import matplotlib.pyplot as plt
plt.plot(np.array(genP1)[:,0])

print('done')

