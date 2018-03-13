
from runSimulation import runSimulation
import sys
import os
here = os.path.dirname(os.path.realpath(__file__))
startInd = 345*24*3600
stopInd = 350*24*3600
runSimulation(here + '/../../GBSProjects/Igiugig', [startInd,stopInd])