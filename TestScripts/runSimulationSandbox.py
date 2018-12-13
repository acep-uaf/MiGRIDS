
from MicroGRIDS.Model.Operational.runSimulation import runSimulation
import sys
import os
here = os.path.dirname(os.path.realpath(__file__))
runSimulation(here + '/../GBSProjects/StMary/OutputData/Set16f')
