
# create instance
import os
from random import randint
from WindTurbine import WindTurbine
wtgID = 1
wtgP = 0
wtgQ = 0
wtgState = 0
timeStep = 1
wtgDescriptor = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\wtg1Descriptor.xml'
windSpeed = []
for i in range(10000):
    windSpeed.append(randint(0,600))

Wtg1 = WindTurbine(wtgID, wtgP, wtgQ, windSpeed, wtgState, timeStep, wtgDescriptor)
Wtg1.wtgState = 2

for i in range(10000):
    Wtg1.checkOperatingConditions()



Wtg1.wtgP = 10


