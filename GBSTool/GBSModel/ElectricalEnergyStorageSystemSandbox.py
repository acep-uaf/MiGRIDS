# create instance
import os
import numpy as np
from ElectricalEnergyStorageSystem import ElectricalEnergyStorageSystem
from matplotlib import cm
eesIDS = [0,1]
eesP = [0]*2
eesQ = [0]*2
eesSOC = [0.5]*2
eesStates = [2]*2
eesSRC = [100]*2
timeStep = 1
eesDescriptor = ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\Components\ees0Descriptor.xml']\
                + ['C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\Components\ees1Descriptor.xml']
eesDispatch = 'eesDispatch1'
eess1 = ElectricalEnergyStorageSystem(eesIDS, eesP, eesQ, eesSOC, eesStates, eesSRC, timeStep, eesDescriptor, eesDispatch)

Pdis = []
PdisSetPoint = []
SOC = []
eesPoutAvail = []
eesPinAvail = []
Ploss = []
eesPScheduleMax = []
SRC = []
x = 0 # keep track of iteration
for i in range(10000):
    P = (np.random.rand() - 0.5) * eess1.eesPOutMax + np.sin(np.pi*x/1000)*eess1.eesPOutMax/2
    #P = min([P, max([sum(eess1.eesPoutAvail), 0])])
    eess1.runEesDispatch(P,0,100)
    # save to array
    PdisSetPoint.append(P)
    Pdis.append(eess1.eesP[:])
    SOC.append(eess1.eesSOC[:])
    eesPoutAvail.append(eess1.eesPoutAvail[:])
    eesPinAvail.append(eess1.eesPinAvail[:])
    Ploss.append(eess1.eesPloss[:])
    eess1.updateEesPScheduleMax()
    eesPScheduleMax.append(eess1.eesPScheduleMax[:])
    SRC.append(eess1.eesSRC[:])
    x += 1

print('done')

import matplotlib.pyplot as plt
plt.plot(SOC)
plt.plot(Ploss)
plt.plot(Pdis)
plt.plot(eesPScheduleMax)
plt.plot(SRC)


eess1.runEesDispatch(P,0,100)