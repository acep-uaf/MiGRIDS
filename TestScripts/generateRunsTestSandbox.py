from generateRunsTest import generateRuns
import os
here = os.path.dirname(os.path.realpath(__file__))
generateRuns(os.path.join(here,"../GBSProjects/StMary/OutputData/Set19"))
#generateRuns(here + '/../../GBSProjects/ControlProject1/OutputData/SetBaseLine')