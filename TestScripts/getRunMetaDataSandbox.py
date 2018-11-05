
from MicroGRIDS.Analyzer.PerformanceAnalyzers.getRunMetaData import getRunMetaData
import os
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../GBSProjects/StMary/OutputData/Set16e")
runs = 'all'
getRunMetaData(projectSetDir,runs)

