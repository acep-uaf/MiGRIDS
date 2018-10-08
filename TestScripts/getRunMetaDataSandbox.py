
from GBSAnalyzer.PerformanceAnalyzers.getRunMetaData import getRunMetaData
import os
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../GBSProjects/SampleProject1/OutputData/Set0")
runs = range(6)
getRunMetaData(projectSetDir,runs)

