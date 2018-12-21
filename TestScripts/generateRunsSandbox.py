from MiGRIDS.Model.Operational.generateRuns import generateRuns
import os
here = os.path.dirname(os.path.realpath(__file__))
generateRuns(os.path.join(here,"../MiGRIDSProjects/testProject/OutputData/Set0"))
