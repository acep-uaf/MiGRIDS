
from MicroGRIDS.Analyzer.DataRetrievers.plotSetResult import plotSetResult
import os
L_gal = 3.78541
kg_L = 0.875
plotResValues = {'Generator Import [GWh]':{'Generator Import kWh':'+',1000000:'/'},'Generator Charging [GWh]':{'Generator Charging kWh':'+',1000000:'/'},
                 'Generator Switching':'Generator Switching','Generator Loading':'Generator Loading','Diesel-off time [h]':'Diesel-off time h',
           'Generator Cumulative Run time [h]':'Generator Cumulative Run time h','Generator Fuel Consumption [kgal]':{'Generator Fuel Consumption kg':'+',1000:'/',kg_L:'/',L_gal:'/'},
                 'Generator Fuel Efficiency [kWh/gal]':{'Generator Import kWh':'+', 'Generator Charging kWh':'+','Generator Fuel Consumption kg':'/',kg_L:'*',L_gal:'*'},
                 'Generator Cumulative Capacity Run Time [GWh]':{'Generator Cumulative Capacity Run Time kWh':'+',1000000:'/'},'Generator Overloading Time [h]':'Generator Overloading Time h',
           'Generator Overloading [kWh]':'Generator Overloading kWh','Wind Power Import [GWh]':{'Wind Power Import kWh':'+',1000000:'/'},'Wind Power Charging [MWh]':{'Wind Power Charging kWh':'+',1000:'/'},
                 'Wind Power Spill [GWh]':{'Wind Power Spill kWh':'+',1000000:'/'},'GBS Discharge [MWh]':{'Energy Storage Discharge kWh':'+',1000:'/'},
           'GBS SRC Provided [GWh]':{'Energy Storage SRC kWh':'+',1000000:'/'},'GBS Overloading Time [h]':'Energy Storage Overloading Time h','GBS Overloading [kWh]':'Energy Storage Overloading kWh',
           'Thermal Energy Storage Throughput [GWh]':{'Thermal Energy Storage Throughput kWh':'+',1000000:'/'},
                 'Total Generator Output [GWh]':{'Generator Import kWh':'+', 'Generator Charging kWh':'+',1000000:'/'},
                 'Total Wind Output [GWh]':{'Thermal Energy Storage Throughput kWh':'+', 'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'},
                 'Total Wind Output (Electrical Loads) [GWh]':{'Wind Power Import kWh':'+', 'Wind Power Charging kWh':'+',1000000:'/'},
                 'GBS Equivalent Cycles':{'Energy Storage Discharge kWh':'x', 'ees0.PInMaxPa.value':'y', 'ees0.ratedDuration.value':'z',
                                          'eqn':'#x#/(#y#*#z#/3600)'},'Mean Individual Online Generator Capacity [kW]':{'Generator Cumulative Capacity Run Time kWh':'+','Generator Cumulative Run time h':'/'},
                 }

# subtract from base: 0 - do not subtract or add, but if base case is specified, place at the begining
# 1 - subtract value from base -> decrease from base case
# 2 - subtract base from value -> increase from base case

subtractFromBase = [0]*len(plotResValues)

plotAttr = 'ees0.POutMaxPa.value'
plotAttrName = 'GBS Rated Power (kW)'
plotResName, plotRes = zip(*plotResValues.items())
otherAttr = ['ees0.ratedDuration.value']
otherAttrNames = {'ees0.ratedDuration.value':'GBS Rated Duration (s)'}
otherAttrVal = [] #[[500,750,1000]]
here = os.path.dirname(os.path.realpath(__file__))
projectSetDir = os.path.join(here,"../GBSProjects/StMary/OutputData/Set16f")
baseSet =  17
baseRun =  0
for pR,pRN, sFB in zip(plotRes,plotResName,subtractFromBase):
    plotSetResult(pR,plotAttr, projectSetDir = projectSetDir, otherAttr = otherAttr,otherAttrVal = otherAttrVal,
                  baseSet = baseSet, baseRun = baseRun, subtractFromBase = sFB, removeSingleOtherAttr = True,
                  alwaysUseMarkers = True, plotResName= pRN, plotAttrName = plotAttrName,
                  otherAttrNames = otherAttrNames)