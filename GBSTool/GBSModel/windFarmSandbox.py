
# create instance
import os
from random import randint
from Windfarm import Windfarm
wtgIDs = [1,2,3,4]
wtgP = [0]*4
wtgQ = [0]*4
wtgStates = [2]*4
timeStep = 1
wtgDescriptor = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\wtg1Descriptor.xml']*4
windSpeed = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg1WS.nc',
'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg2WS.nc',
'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg3WS.nc',
'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg4WS.nc']

WF1 = Windfarm(wtgIDs, windSpeed, wtgStates, timeStep, wtgDescriptor)

wtg0P = []
wtg1P = []
wtg2P = []
for i in range(10000-1):
    WF1.wtgDispatch(70,0)
    wtg0P.append(WF1.windTurbines[0].wtgP)
    wtg1P.append(WF1.windTurbines[1].wtgP)
    wtg2P.append(WF1.windTurbines[2].wtgP)

# plot results
import matplotlib.pyplot as plt
plt.plot(wtg0P)
plt.plot(wtg1P)
plt.plot(wtg2P)
plt.plot(WF1.windTurbines[0].windPower)
plt.show()

print('done')


