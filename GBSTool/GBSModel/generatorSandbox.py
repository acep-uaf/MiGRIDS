
# create instance
import os
from Generator import Generator
genID = 1
genP = 0
genQ = 0
genState = 0
timeStep = 1
genDescriptor = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\Components\gen1Descriptor.xml'
Generator1 = Generator(genID, genP, genQ, genState, timeStep, genDescriptor)

Generator1.genP = 10