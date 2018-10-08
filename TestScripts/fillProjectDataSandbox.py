
from GBSInputHandler.fillProjectData import fillProjectData
import os
here = os.path.dirname(os.path.realpath(__file__))
fillProjectData(os.path.join(here,"../GBSProjects/SampleProject1"))