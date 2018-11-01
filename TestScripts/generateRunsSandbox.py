from MicroGRIDS.Model.Operational.generateRuns import generateRuns
import os
here = os.path.dirname(os.path.realpath(__file__))
generateRuns(os.path.join(here,"../GBSProjects/StMary/OutputData/Set16f"))
