
from MicroGRIDS.InputHandler.initiateProjectSet import initiateSet
import os
here = os.path.dirname(os.path.realpath(__file__))
projectDir = 'testProject'
setID = '0'
initiateSet(projectDir,setID)