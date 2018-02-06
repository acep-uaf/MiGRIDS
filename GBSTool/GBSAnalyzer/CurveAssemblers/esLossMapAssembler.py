# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu Alaska Center for Energy and Power
# Date: February 1, 2018 -->
# License: MIT License (see LICENSE file of this package for more information)


# *** General Imports ***
from scipy.interpolate import interp2d
import numpy as np


class esLossMap:
    '''
    This class contains methods to build a dense loss map for energy storage units based on sparser information provided in
        `esDescriptor.xml`.  There ...

    '''

    # TODO: write

    # Constructor
    def __init__(self):
        # ******* INPUT VARIABLES *******
        # list of tuples for a loss map. (power [pu], SOC [pu], loss [pu of power], ambient temperature [K])
        self.lossMapDataPoints = []

        # Maximum output power [kW]. This is the will be the upper limit of the power axis
        self.pInMax = 0
        # Maximum input power [kW]. This is the will be the upper limit of the power axis
        self.pOutMax = 0
        # Maximum energy capacity in kWs
        self.eMax = 0

        # ******* INTERNAL VARIABLES *******
        # Coordinates for interpolation
        self.coords = []

        # ******* OUTPUT VARIABLES *******
        # The dense lossMap with units [kW, kg/s]
        self.lossMap = []
        # The dense lossMap, but with integer values only.
        self.lossMapInt = []
        # loss map array power vector
        self.P = []
        # loss map array energy vector
        self.E = []
        # loss map array temperature vector
        self.Temp = []
        # loss map array with dimensions power x energy
        self.loss = np.array([])
        # an array, with same dimensions as the loss map, with the max amount of time that the es can charge or discharge
        # at a given power for starting at a given state of charge
        self.maxDischTime = np.array([])

    def checkInputs(self):
        '''
        Makes sure data inputs are self-consistent. **Does not** check for physical validity of data.

        :raises ValueError: for various data inconsistencies or missing values.

        :return:
        '''
        # make copy of the input
        inptDataPoints = self.lossMapDataPoints

        # Check if data was initialized at all.
        if not inptDataPoints:
            raise ValueError('Loss map is empty list.')
        elif self.pInMax == 0:
            raise ValueError('Maximum input power is not configured, or set to 0.')
        elif self.pOutMax == 0:
            raise ValueError('Maximum output power is not configured, or set to 0.')
        elif self.eMax == 0:
            raise ValueError('Maximum energy capacoty is not configured, or set to 0.')

        # Check for negative values in loss, temperature and soc - there shouldn't be any
        for tpls in inptDataPoints:
            if any(n < 0 for n in tpls[1:]):
                raise ValueError('SOC, Loss or temperature inputs contain negative values.')

        # Make a copy of the input

        # Sort the new list of tuples based on power levels.
        #inptDataPoints.sort()

        # Check for duplicates and clean up if possible.
        # TODO: implement

        self.coords = inptDataPoints

    def linearInterpolation(self,chargeRate, pStep = 1, eStep = 3600, tStep = 1):
        # chargeRate is the maximum fraction of the remaining energy storage capacity that can be charged in 1 second,
        # or remaining energy storage capacity that can be discharged in 1 second, units are pu/sec
        # pStep, eStep and tStep are the steps to be used in the loss map for power, energy and temperature. Units are
        # kW, kWs and K.

        # unzip into individual arrays
        pDataPoints, eDataPoints, lossDataPoints, tempAmbDataPoints = zip(*self.coords)

        if len(set(tempAmbDataPoints)) < 2: # if not more than one temperature defined, only 2d array (power and energy)
            # create interpolation function
            fn = interp2d(eDataPoints,pDataPoints,lossDataPoints)
            # create filled power and energy arrays
            if self.pInMax > 0:  # check if a positive value was given
                usePinMax = - self.pInMax
            else:
                usePinMax = self.pInMax
            self.P = range(int(usePinMax), int(self.pOutMax + pStep), int(pStep))
            self.E = range(0, int(self.eMax + eStep), int(eStep))
            self.Temp = tempAmbDataPoints
            # create new filled loss array.
            self.loss = np.array(fn(self.E,self.P)) # array with size power x energy

            # create another array with the maximum amount of time that can be spent charging or discharging at a power
            # given a state of charge
            # first, create an array with the time it takes to reach the next energy bin, taking into account losses
            t = np.zeros([len(self.P), len(self.E)]) # initiate array
            t[:] = np.nan # to nan
            for idxE, E in enumerate(self.E): # for every energy level
                for idxP, P in enumerate(self.P): # for every power
                    # if the power is within the chargeRate bounds
                    if (P >= (E - self.eMax) * chargeRate) & (P <= E * chargeRate):
                        if P > 0:  # if discharging
                            # find the amount of time to get to the next energy bin
                            t[idxP, idxE] = (eStep) / (P + self.loss[idxP, idxE])
                        elif np.round(P) < 0: # if charging
                            # find the amount of time to get to the next energy bin
                            t[idxP, idxE] = -(eStep) / (P + self.loss[idxP, idxE])
            # now use the array of the time it takes to get to the next bin and calculate array of the max amount of
            # time the ES can charge or discharge at a certain power, starting at a certain energy level
            self.maxDischTime = np.zeros([len(self.P), len(self.E)])  # initiate array
            self.maxDischTime[:] = np.nan  # to nan
            for idxE, E in enumerate(self.E):  # for every energy level
                for idxP, P in enumerate(self.P):  # for every power
                    if t[idxP,idxE] != np.nan: # if nan, leave as is. a max time does not make sense here
                        if P > 0: # if discharging
                            # the total discharge time is the sum of the time taken to get to each consecutive bin.
                            self.maxDischTime[idxP,idxE] = np.nansum(t[idxP,:idxE])
                        if P < 0: # if charging
                            # the total charge time is the sum of the time taken to get to each consecutive bin.
                            self.maxDischTime[idxP,idxE] = np.nansum(t[idxP,idxE:])

        else: # if more than one temperature defined
            # TODO: implement
            self.P = []
            self.E = []
            self.Temp = []
            self.loss = np.array([])