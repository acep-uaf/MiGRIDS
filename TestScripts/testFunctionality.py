from MiGRIDS.Model.Operational.initiateProjectSet import initiateSet
import os
here = os.path.dirname(os.path.realpath(__file__))
projectDir = 'OptimizerTestHarness'
setID = 'Test'
initiateSet(projectDir,setID)