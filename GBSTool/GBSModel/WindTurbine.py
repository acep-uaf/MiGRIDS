# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup
import sys
sys.path.append('../')
from GBSAnalyzer.CurveAssemblers.wtgPowerCurveAssembler import WindPowerCurve
from bisect import bisect_left

class WindTurbine:
    """
    Wind turbine class: contains all necessary information for a single wind turbine. Multiple wind turbines are
    aggregated in a Windfarm object (see Windfarm.py), which further is aggregated in the SystemOperations object (see
    SystemOperations.py).

    :param wtgID: internal id used in the Windfarm for tracking wind turbine objects. *type int*
    :var wtgName: name given in wtgDescriptor file and is merely uswed to trace back to that. *type string*
    :var wtgP: Current real power level, units: kW. *type float*
    :var wtgQ: Current reactive power level, units: kW. *type float*
    :var wtgState: Wind turbine operating state 0 - off, 1 - starting, 2 - online.
    :var wtgPMax: Real power nameplate capacity, units: kW. *type float*
    :var wtgQMax: Reactive power nameplate capacity, units: kvar. *type float*
    :var wtgPAvail: Available real power capacity, units: kW. *type float*
    :var wtgQAvail: Available reactive power capacity, units: kvar. *type float*
    :var wtgStartTime: Time to start the wind turbine, units: s. *type int*
    :var wtgPowerCurve: Power curve of the wind turbine, tuples of [kW, m/s]. *type list(float,float)*
    :var wtgRunTimeAct: Run time since last start, units: s. *type int*
    :var wtgRunTimeTot: Cummulative run time since model start, units: s. *type int*

    :method __init__: Constructor with additional instructions
    :method wtgDescriptorParser: parses the necessary data from the wtgDescriptor.xml file provided.

    :returns:
    """



    # Constructor
    def __init__(self, wtgID, wtgP, wtgQ, windSpeed, wtgState, timeStep, wtgDescriptor):
        """
        Constructor used for the initialization of an object within windfarm list of wind turbines.

        :param wtgID:
        :param wtgP:
        :param wtgQ:
        :param wtgDescriptor:
        """
        # Write initial values to internal variables.
        self.wtgID = wtgID # internal id used in the Windfarm for tracking wind turbine objects. *type int*
        self.wtgP = wtgP # Current real power level [kW] *type float*
        self.wtgQ = wtgQ # Current reactive power level [kvar] *type float*
        self.wtgState = wtgState  # Wind turbine operating state [dimensionless, index]. 0 - off, 1 - starting, 2 - online.
        self.timeStep = timeStep
        # grab data from descriptor file
        self.wtgDescriptorParser(windSpeed,wtgDescriptor)

        self.wtgPAvail = 0  # the available power from the wind [kW]
        self.wtgQAvail = 0  # the available power form the wind [kar]
        self.wtgStartTime = 0  # Time to start the wind turbine [s]

        self.wtgRunTimeAct = 0  # Run time since last start [s]
        self.wtgRunTimeTot = 0  # Cummulative run time since model start [s]
        self.wtgStartTimeAct = 0 # time spent starting up since last start [s]
        self.step = 0 # this keeps track of which step in the time series we are on

    def wtgDescriptorParser(self, windSpeed, wtgDescriptor):
        """
        wtgDescriptorParser: parses the necessary data from the wtgDescriptor.xml file provided.

        :param wtgDescriptor: relative path and file name of wtgDescriptor.xml-file that is used to populate static
        information

        :return:
        """

        # read xml file
        wtgDescriptorFile = open(wtgDescriptor, "r")
        wtgDescriptorXml = wtgDescriptorFile.read()
        wtgDescriptorFile.close()
        wtgSoup = Soup(wtgDescriptorXml, "xml")


        # Dig through the tree for the required data
        self.wtgName = wtgSoup.component.get('name')
        self.wtgPMax = float(wtgSoup.POutMaxPa.get('value')) # Nameplate capacity [kW]
        self.wtgQMax = float(wtgSoup.QOutMaxPa.get('value'))  # Nameplate capacity [kvar]

        # Handle the fuel curve interpolation
        powerCurvePPuInpt = wtgSoup.powerCurveDataPoints.pPu.get('value').split()
        powerCurveWsInpt = wtgSoup.powerCurveDataPoints.ws.get('value').split()
        if len(powerCurvePPuInpt) != len(powerCurveWsInpt):  # check that both input lists are of the same length
            raise ValueError('Power curve calculation error: Power and wind speed lists are not of same length.')

        powerCurveData = []
        for idx, item in enumerate(powerCurvePPuInpt):
            powerCurveData.append((float(powerCurveWsInpt[idx]), self.wtgPMax * float(powerCurvePPuInpt[idx])))
        wtgPC = WindPowerCurve()
        wtgPC.powerCurveDataPoints = powerCurveData
        wtgPC.cutInWindSpeed = float(wtgSoup.cutInWindSpeed.get('value')) # Cut-in wind speed, float, m/s
        wtgPC.cutOutWindSpeedMin = float(wtgSoup.cutOutWindSpeedMin.get('value')) # Cut-out wind speed min, float, m/s
        wtgPC.cutOutWindSpeedMax = float(wtgSoup.cutOutWindSpeedMax.get('value')) # Cut-out wind speed max, float, m/s
        wtgPC.POutMaxPa = self.wtgPMax # Nameplate power, float, kW
        wtgPC.cubicSplineCurveEstimator()
        self.wtgPowerCurve = wtgPC.powerCurve

        # generate possible wind power time series
        # get the generator fuel consumption at this loading for this combination
        PCws, PCpower = zip(*self.wtgPowerCurve)  # separate out the windspeed and power
        # iterate through wind speeds
        self.windPower = [] #initiate wind power list
        for WS in windSpeed:
            # bisect left gives the index of the last list item to not be over the number being searched for. it is faster than using min
            # this finds the associated fuel consumption to the scheduled load for this combination
            self.windPower.append(PCpower[self.findClosestInd(PCws, WS)])

    # this finds the closest index of item in the list 'L'
    def findClosestInd(self,L,item):
        ind = bisect_left(L, item)
        # check which list value is closest, the value below or above the item
        if ind == len(L):
            return ind - 1
        elif (item - L[ind-1]) < (L[ind] - item):
            return ind-1
        else:
            return ind

    def checkOperatingConditions(self):
        if self.wtgState == 2: # if running online
            self.wtgPAvail = self.windPower[self.step]
            self.wtgRunTimeAct += self.timeStep
            self.wtgRunTimeTot += self.timeStep
        elif self.wtgState == 1: # if starting up
            self.wtgPAvail = 0 # not available to produce power yet
            self.wtgQAvail = 0
            self.wtgStartTimeAct += self.timeStep
            self.wtgRunTimeAct = 0 # reset run time counter
        else: # if off
            # no power available and reset counters
            self.wtgPAvail = 0
            self.wtgQAvail = 0
            self.wtgStartTimeAct = 0
            self.wtgRunTimeAct = 0
        self.step += 1 # increment which step we are on