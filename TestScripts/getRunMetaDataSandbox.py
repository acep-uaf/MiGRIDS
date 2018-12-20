
from MicroGRIDS.Analyzer.PerformanceAnalyzers.getRunMetaData import getRunMetaData
import os
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../MicroGRIDSProjects/SampleProject1/OutputData/Set0")
runs = 'all'
getRunMetaData(projectSetDir,runs)

