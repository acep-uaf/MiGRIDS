
from MicroGRIDS.Analyzer.PerformanceAnalyzers.getRunMetaData import getRunMetaData
import os
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../GBSProjects/StMary/OutputData/Set16b")
runs = range(21)
getRunMetaData(projectSetDir,runs)

