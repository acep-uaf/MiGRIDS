

# create instance
import os
from ElectricalStorage import ElectricalEnergyStorage
eesID = 1
eesP = 0
eesQ = 0
eesSOC = 0.5
eesState = 0
eesSRC = 100
timeStep = 1
eesDescriptor = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\\test\InputData\Components\ees1Descriptor.xml'
Ees1 = ElectricalEnergyStorage(eesID, eesP, eesQ, eesSOC, eesState, eesSRC, timeStep, eesDescriptor)
Ees1.eesState = 2

print('done')
