
from MicroGRIDS.Analyzer.PerformanceAnalyzers.getRunMetaData import getRunMetaData
import os
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../GBSProjects/Igiugig/OutputData/Set4")
runs = 'all'
getRunMetaData(projectSetDir,runs)

