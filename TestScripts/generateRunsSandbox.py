from GBSModel.Operational.generateRuns import generateRuns
import os
here = os.path.dirname(os.path.realpath(__file__))
generateRuns(os.path.join(here,"../GBSProjects/SampleProject1/OutputData/Set0"))
