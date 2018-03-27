# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import os
import sys

# General imports
from bs4 import BeautifulSoup as Soup

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
from GBSAnalyzer.CurveAssemblers.wtgPowerCurveAssembler import WindPowerCurve
from bisect import bisect_left
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile
from getIntListIndex import getIntListIndex
from getSeriesIndices import getSeriesIndices
import numpy as np
from scipy.interpolate import interp1d
from distutils.util import strtobool

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
    def __init__(self, wtgID, windSpeedDir, wtgState, timeStep, wtgDescriptor, runTimeSteps = 'all'):
        """
        Constructor used for the initialization of an object within windfarm list of wind turbines.

        :param wtgID:
        :param wtgDescriptor:
        """
        # Write initial values to internal variables.
        self.wtgID = wtgID # internal id used in the Windfarm for tracking wind turbine objects. *type int*
        self.wtgP = 0 # Current real power level [kW] *type float*
        self.wtgQ = 0 # Current reactive power level [kvar] *type float*
        self.wtgState = wtgState  # Wind turbine operating state [dimensionless, index]. 0 - off, 1 - starting, 2 - online.
        self.timeStep = timeStep
        self.runTimeSteps = runTimeSteps # the input to calculate which timesteps to run in the simulation
        # grab data from descriptor file
        self.wtgDescriptorParser(windSpeedDir,wtgDescriptor)

        self.wtgPAvail = 0  # the available power from the wind [kW]
        self.wtgQAvail = 0  # the available power form the wind [kar]
        self.wtgStartTime = 0  # Time to start the wind turbine [s]

        self.wtgRunTimeAct = 0  # Run time since last start [s]
        self.wtgRunTimeTot = 0  # Cummulative run time since model start [s]
        self.wtgStartTimeAct = 0 # time spent starting up since last start [s]
        self.step = 0 # this keeps track of which step in the time series we are on
        self.wtgSpilledWind = [] # time series of spilled wind power
        self.wtgSpilledWindCum = 0 # amount of spilled wind power in last wtgCheckWindPowerTime seconds
        self.wtgSpilledWindFlag = False # indicates over spilled wind power limit

        # initiate runtime values
        self.checkOperatingConditions()

    def wtgDescriptorParser(self, windSpeedDir, wtgDescriptor):
        """
        wtgDescriptorParser: parses the necessary data from the wtgDescriptor.xml file provided.

        :param wtgDescriptor: relative path and file name of wtgDescriptor.xml-file that is used to populate static
        information

        :return:
        """

        print(wtgDescriptor)

        # read xml file
        wtgDescriptorFile = open(wtgDescriptor, "r")
        wtgDescriptorXml = wtgDescriptorFile.read()
        wtgDescriptorFile.close()
        wtgSoup = Soup(wtgDescriptorXml, "xml")


        # Dig through the tree for the required data
        self.wtgName = wtgSoup.component.get('name')
        self.wtgPMax = float(wtgSoup.POutMaxPa.get('value')) # Nameplate capacity [kW]
        self.wtgQMax = float(wtgSoup.QOutMaxPa.get('value'))  # Nameplate capacity [kvar]
        self.wtgCheckWindTime = float(wtgSoup.checkWindTime.get('value'))  # time to check spilled wind power over
        self.wtgSpilledWindLimit = float(
            wtgSoup.spilledWindLimit.get('value'))  # time to check spilled wind power over
        self.wtgRecalculateWtgPAvail = strtobool(
            wtgSoup.recalculateWtgPAvail.get('value'))  # bool whether to recalculate wind power from wind speeds

        # Handle the fuel curve interpolation
        if self.wtgRecalculateWtgPAvail:
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
            self.wtgPowerCurve = wtgPC.powerCurveInt

        # check if there are wind power files in the wind speed directory
        windSpeedFile = os.path.join(windSpeedDir,'wtg'+str(self.wtgID)+'WS.nc')
        windPowerFile = os.path.join(windSpeedDir,'wtg'+str(self.wtgID)+'PAvail.nc')
        if os.path.isfile(windPowerFile) and not self.wtgRecalculateWtgPAvail:
            # if there is, then read it
            NCF = readNCFile(windPowerFile)
            windPower = np.array(NCF.value)*NCF.scale + NCF.offset
            windTime = NCF.time
        elif os.path.isfile(windSpeedFile):
            # read wind speed file
            NCF = readNCFile(windSpeedFile)
            windSpeed = np.array(NCF.value) * NCF.scale + NCF.offset
            windTime = NCF.time
            # check if any nan values
            if any(np.isnan(NCF.time)) or any(np.isnan(NCF.value)):
                raise ValueError(
                    'There are nan values in the wind files.')
            # check the units for time
            elif NCF.timeUnits.lower() != 's' and NCF.timeUnits.lower() != 'sec' and NCF.timeUnits.lower() != 'seconds':
                raise ValueError('The units for time must be s.')
                # check time step to make sure within +- 10% of timeStep input
                # this will have a problem with daylight savings
                # elif min(np.diff(NCF.time)) < 0.9 * timeStep or max(np.diff(NCF.time)) > 1.1 * timeStep:
                #    raise ValueError(
                #       'The difference in the time stamps is more than the 10% different than the time step defined for '
                #       'this simulation ({} s). The timestamps should be in epoch format.'.format(timeStep))
            # generate possible wind power time series
            # get the generator fuel consumption at this loading for this combination
            PCws, PCpower = zip(*self.wtgPowerCurve)  # separate out the windspeed and power
            # get wind power
            windPower = self.getWP(PCpower,PCws,windSpeed, wtgPC.wsScale)
            # save nc file to avoid having to calculate for future simulations
            #writeNCFile(NCF.time[:], windPower, 1, 0, 'kW', os.path.join(windSpeedDir,'wtg'+str(self.wtgID)+'WP.nc'))
        else:
            raise ValueError('There is no wind speed file in the specified directory.')

        # interpolate wind power according to the desired timestep
        f = interp1d(windTime,windPower)
        num = int(len(windTime) / self.timeStep)
        windTimeNew = np.linspace(windTime[0], windTime[-1], num)
        windPowerNew = f(windTimeNew)
        # get the indices of the timesteps to simulate
        indRun = getSeriesIndices(self.runTimeSteps, len(windPowerNew))
        self.windPower = windPowerNew[indRun]

    # get wind power available from wind speeds and power curve
    # using integer list indexing is much faster than np.searchsorted
    # PCws is an interger list, with no missing values, of wind speeds in 0.1 m/s
    # PCpower is the corresonding power in kW
    # windSpeed is a list of windspeeds in m/s
    def getWP(self,PCpower,PCws,windSpeed, wsScale):
        windPower = []
        for WS in windSpeed:
            # get the index of the wind speed
            idx = getIntListIndex(WS*wsScale,PCws)
            # append the corresponding wind power
            windPower.append(PCpower[idx])
        return windPower


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
            self.wtgPAvail = self.windPower[min([self.step,len(self.windPower)-1])]
            self.wtgRunTimeAct += self.timeStep
            self.wtgRunTimeTot += self.timeStep

            # update spilled wind power time series
            self.wtgSpilledWind.append(max([self.wtgPAvail-self.wtgP, 0]))
            # get the spilled wind power in checkWindPowerTime
            # if the spilled length of time measured spilled wind power over is less than the check time
            if len(self.wtgSpilledWind) > int(self.wtgCheckWindTime/self.timeStep):
                self.wtgSpilledWindCum = self.wtgSpilledWindCum + self.wtgSpilledWind[-1]- self.wtgSpilledWind[-int(self.wtgCheckWindTime/self.timeStep)]
            else:
                self.wtgSpilledWindCum = self.wtgSpilledWindCum + self.wtgSpilledWind[-1]

            # if enough wind spilled, set flag
            if (self.wtgSpilledWindCum > self.wtgSpilledWindLimit) and (self.wtgSpilledWind[-1] > 0):
                self.wtgSpilledWindFlag = True

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