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

    def linearInterpolation(self,pStep = 1, eStep = 3600, tStep = 1):
        # unzip into individual arrays
        pDataPoints, eDataPoints, lossDataPoints, tempAmbDataPoints = zip(*self.coords)

        if len(tempAmbDataPoints) < 2: # if not more than one temperature defined, only 2d array (power and energy)
            # create interpolation function
            fn = interp2d(pDataPoints,eDataPoints,lossDataPoints)
            # create filled power and energy arrays
            if self.pInMax > 0:  # check if a positive value was given
                usePinMax = - self.pInMax
            else:
                usePinMax = self.pInMax
            self.P = range(int(usePinMax), int(self.pOutMax + pStep), int(pStep))
            self.E = range(0, int(self.eMax + eStep), int(eStep))
            self.Temp = tempAmbDataPoints
            # create new filled loss array.
            self.loss = np.array(fn(self.P,self.E))


        else: # if more than one temperature defined
            # TODO: implement
            self.P = []
            self.E = []
            self.Temp = []
            self.loss = np.array([])