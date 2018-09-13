
from GBSTool.GBSAnalyzer.DataRetrievers.plotSetResultPdf import plotSetResultPdf

projectSetDir = 'C:\\Users\\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\OutputData\Set16a'
runs = [0,4,7,11,14,18]
legTxt = ['500 kW/1 min GBS','500 kW/5 min GBS', '750 kW/1 min GBS', '750 kW/5 min GBS', '1000 kW/1 min GBS', '1000 kW/5 min GBS']
timeStep = 10 # seconds

plotSetResultPdf(projectSetDir, runs, legTxt,timeStep)