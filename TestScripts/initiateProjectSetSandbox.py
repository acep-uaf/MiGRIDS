
from MicroGRIDS.Model.Operational.initiateProjectSet import initiateSet
import os
here = os.path.dirname(os.path.realpath(__file__))
projectDir = 'testProject'
setID = '1'
initiateSet(projectDir,setID)