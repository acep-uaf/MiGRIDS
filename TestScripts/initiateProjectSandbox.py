
from MiGRIDS.InputHandler.initiateProject import initiateProject
import os
here = os.path.dirname(os.path.realpath(__file__))
projectName = 'testProject'
componentNames = ['ees0','ees1','tes0','gen0','gen1','gen2','wtg0','wtg1','load0']
initiateProject(projectName,componentNames)