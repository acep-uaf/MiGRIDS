# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu Alaska Center for Energy and Power
# Date: February 1, 2018 -->
# License: MIT License (see LICENSE file of this package for more information)


# *** General Imports ***
from scipy.interpolate import CubicSpline
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
        # Maximum temperature [K] defined in the loss map array, if max and min are the same, then temperature is not
        # factored into loss
        self.tMax = 298
        # Minimum temperature [K]
        self.tMin = 298

        # ******* INTERNAL VARIABLES *******
        # Coordinates for interpolation
        self.coords = []

        # ******* OUTPUT VARIABLES *******
        # The dense lossMap with units [kW, kg/s]
        self.lossMap = []
        # The dense lossMap, but with integer values only.
        self.lossMapInt = []

    def checkInputs(self):
        '''
        Makes sure data inputs are self-consistent. **Does not** check for physical validity of data.

        :raises ValueError: for various data inconsistencies or missing values.

        :return:
        '''


        # Check if data was initialized at all.
        if not self.lossMapDataPoints:
            raise ValueError('Loss map is empty list.')
        elif self.pInMax == 0:
            raise ValueError('Maximum input power is not configured, or set to 0.')
        elif self.pOutMax == 0:
            raise ValueError('Maximum output power is not configured, or set to 0.')
        elif self.eMax == 0:
            raise ValueError('Maximum energy capacoty is not configured, or set to 0.')

        # Check for negative values in loss, temperature and soc - there shouldn't be any
        for tpls in self.lossMapDataPoints:
            if any(n < 0 for n in tpls[1:]):
                raise ValueError('SOC, Loss or temperature inputs contain negative values.')

        # Make a copy of the input
        inptDataPoints = self.fuelCurveDataPoints
        # Sort the new list of tuples based on power levels.
        inptDataPoints.sort()

        # Check for duplicates and clean up if possible.
        # TODO: implement

        self.coords = inptDataPoints

    def linearInterpolation(self,pStep = 1, eStep = 1, tStep = 1):
        # unzip into individual arrays
        pPu, ePu, loss, tempAmb = zip(*self.coords)
        pPu = np.array(pPu)
        ePu = np.array(ePu)
        loss = np.array(loss)
        tempAmb = np.array(tempAmb)

        # create 3D array with power, soc and temp axes
        indPsort = np.argsort(pPu)
        pPuSorted = sorted(pPu)
        indPsort = np.argsort(pPu)
        pPuSorted = sorted(pPu)