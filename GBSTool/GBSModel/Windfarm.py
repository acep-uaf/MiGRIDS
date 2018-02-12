# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

from WindTurbine import WindTurbine
import itertools
import sys
import numpy as np
sys.path.append('../')
from GBSAnalyzer.CurveAssemblers.wtgPowerCurveAssembler import WindPowerCurve
from bisect import bisect_left


class Windfarm:
    # __init()__ Class constructor. Initiates the setup of the individual wind turbines as per the initial input.
    # Inputs:
    # self - self reference, always required in constructor
    # wtgIDS - list of wtg IDs, which should be integers
    # wtgP - list of wtg real power levels for respective wtg listed in genIDS
    # wtgQ - list of wtg reactive power levels for respective wtg listed in wtgIDS
    # wtgStates - list of wind turbine operating states 0 - off, 1 - starting, 2 - online.
    # wtgDescriptor - list of generator descriptor XML files for the respective generators listed in genIDS, this should
    #   be a string with a relative path and file name, e.g., /InputData/Components/wtg1Descriptor.xml
    def __init__(self, wtgIDS, windSpeed, wtgStates, timeStep, wtgDescriptor):
        # check to make sure same length data coming in
        if not len(wtgIDS) == len(wtgStates):
            raise ValueError('The length wtgIDS, wtgP, wtgQ and wtgStates inputs to Windfarm must be equal.')

        # ************Windfarm variables**********************
        # List of wtg and their respective IDs
        self.windTurbines = []
        self.wtgIDS = wtgIDS

        # total capacities
        self.wtgPMax = 0
        self.wtgQMax = 0

        # WTG dispatch object
        self.wtgDispatchType = 1  # wtg dispatch to use, 1 for proportional

        # Cumulative operational data
        # Actual loadings
        self.wtgP = []
        self.wtgQ = []
        # Total available wtg power without new dispatch
        self.wtgPAvail = []
        self.wtgQAvail = []

        # Populate the list of wtg with windTurbine objects
        for idx, wtgID in enumerate(wtgIDS):
            # check if only one wind profile was given, or if profiles were given for each turbine (list of lists)
            if isinstance(windSpeed[0],(list,tuple,np.ndarray)):
                # if windSpeed is a list of lists with length greater than one (more than one list) the one for each turbine
                if len(windSpeed) > 1:
                    WS = windSpeed[idx]
                else: # if there is only 1 list, then use for all turbines
                    WS = windSpeed[0]
            else: # if windSpeed is a list of values, not lists, then use for all turbines
                WS = windSpeed
            # Initialize wtg
            self.windTurbines.append(WindTurbine(wtgID, WS, wtgStates[idx], timeStep, wtgDescriptor[idx]))

            # Initial value for wtgP, wtgQ, wtgPAvail and wtgQAvail can be handled while were in this loop
            self.wtgPMax = self.wtgPMax + self.windTurbines[idx].wtgPMax
            self.wtgQMax = self.wtgQMax + self.windTurbines[idx].wtgQMax
            self.wtgP += [self.windTurbines[idx].wtgP]
            self.wtgQ += [self.windTurbines[idx].wtgQ]
            self.wtgPAvail += [self.windTurbines[idx].wtgPAvail]
            self.wtgQAvail += [self.windTurbines[idx].wtgQAvail]

    # wtgDispatch class method. Assigns a loading to each online wind turbine. It will not allow overloading.
    # TODO: some turbines (eg EWT) are able to slow down their rotors to supply overcurrent for a short duration. This can be incorporated
    # Inputs:
    # self - self reference
    # newWtgP - new total wind turbine real load
    # newWtgQ - new total wind turbine reactive load
    def wtgDispatch(self, newWtgP, newWtgQ):
        # check available power

        # dispatch
        if self.wtgDispatchType == 1:  # if proportional loading
            # check available power
            for idx in range(len(self.wtgIDS)):
                # update available power and runtimes
                self.windTurbines[idx].checkOperatingConditions()
                self.wtgPAvail[idx] = self.windTurbines[idx].wtgPAvail
                self.wtgQAvail[idx] = self.windTurbines[idx].wtgQAvail
            # get the loading pu for real and reactive power
            loadingP = np.nanmin([newWtgP / np.sum(self.wtgPAvail),1])  # this is the PU loading of each wtg, limited to 1
            loadingQ = np.nanmin([newWtgQ / np.sum(self.wtgQAvail) ,1]) # this is the PU loading of each wtg
            # cycle through each wtg and update with new P and Q
            for idx in range(len(self.wtgIDS)):
                self.windTurbines[idx].wtgP = loadingP * self.wtgPAvail[idx]
                self.windTurbines[idx].wtgQ = loadingQ * self.wtgQAvail[idx]
                # update the local variable that keeps track of wtg power
                self.wtgP[idx] = self.windTurbines[idx].wtgP
                self.wtgQ[idx] = self.windTurbines[idx].wtgQ
                # TODO: update time with some other metric to measure when enough wind to start turbine. Add this value to the wtgDescriptor.xml
                # TODO: or just take this into account in the wind power profile.
                # check to see if turbines that are starting up are ready to switch online
                if self.windTurbines[idx].wtgStartTimeAct >= self.windTurbines[idx].wtgStartTime:
                    self.windTurbines[idx].wtgState = 2
        else:
            print('The wind turbine dispatch is not supported. ')

