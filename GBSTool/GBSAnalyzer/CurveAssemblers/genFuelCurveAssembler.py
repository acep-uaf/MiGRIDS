# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamcis.com
# Date: September 30, 2017 -->
# License: MIT License (see LICENSE file of this package for more information)


# *** General Imports ***
from scipy.interpolate import CubicSpline
import numpy as np


class GenFuelCurve:
    '''
    This class contains methods to build a dense fuel curve for diesel generators based on sparser information provided in
        `genDescriptor.xml`.  There the fuel curve contains tuples of tags, pPu (power in P.U. referenced to nameplate capacity)
        and massFlow in kg/s. Here the intent is to provide a density of points such that there is a fuel consumption data point
        for each 1 kW increment in power level. For practical reasons, the pPu output curve does include overload values, which
        exhibit a linear extension of the fuel consumption given for pPu = 1.
        Note that the fuel consumption data input assumes that corrections for fuel temperature, fuel type, etc. have
        already been performed.

    '''

    # Constructor
    def __init__(self):
        # ******* INPUT VARIABLES *******
        # Data points give in genDescriptor.xml, list of tuples, [kW, kg/s]
        self.fuelCurveDataPoints = []
        # Maximum overload capacity [kW]. This is used to provide a maximum x-coordinate for the fuel curve
        self.genOverloadPMax = 0

        # ******* INTERNAL VARIABLES *******
        # Coordinates for interpolation
        self.coords = []

        # ******* OUTPUT VARIABLES *******
        # The dense fuel curve with units [kW, kg/s]
        self.fuelCurve = []
        # The dense fuel curve, but with integer values only. Fuel consumption values to be multiplied by 10,000.
        self.fuelCurveInt = []

    def checkInputs(self):
        '''
        Makes sure data inputs are self-consistent. **Does not** check for physical validity of data.

        :raises ValueError: for various data inconsistencies or missing values.

        :return:
        '''

        # Check if data was initialized at all.
        if not self.fuelCurveDataPoints:
            raise ValueError('Fuel curve input is empty list.')
        elif self.genOverloadPMax == 0:
            raise ValueError('Maximum overload power level is not configured, or set to 0.')

        # Check for negative values - there shouldn't be any
        for tpls in self.fuelCurveDataPoints:
            if any(n < 0 for n in tpls):
                raise ValueError('Input data contains negative values.')

        # Make a copy of the input
        inptDataPoints = self.fuelCurveDataPoints
        # Sort the new list of tuples based on power levels.
        inptDataPoints.sort()

        # Check for duplicates and clean up if possible.
        prevVal = (-999, -999)
        for inptDataPoint in inptDataPoints:
            # remove duplicates
            if inptDataPoint[0] == prevVal[0] and inptDataPoint[1] == prevVal[1]:
                inptDataPoints.remove(inptDataPoint)
            # if there's multiple fuel consumption values for the same power value raise an exception
            elif inptDataPoint[0] == prevVal[0] and inptDataPoint[1] != prevVal[1]:
                raise ValueError('Fuel curve data points  ill-defined, multiple fuel use values for single power value.')

            # Copy current to previous value and proceed.
            prevVal = inptDataPoint

        self.coords = inptDataPoints


    def cubicSplineCurveEstimator(self, loadStep = 1):
        '''
        cubicSplineCurveEstimator calculates a cubic spline for the given data points in fuelCurveDataPoints.

        :return:
        '''

        self.checkInputs()
        # Setup x and y coordinates as numpy arrays
        x, y = zip(*self.coords)
        xCoords = np.array(x)
        yCoords = np.array(y)

        # Calculate the cubic spline using the scipy function for this. Boundary conditions are that the outside elements
        # are extensions of the first and last polynomial. This works because we can assume the fuel curve to be fairly
        # linear.
        cs = CubicSpline(xCoords, yCoords, bc_type='not-a-knot', extrapolate=True)

        # To pull an array of values from the cubic spline, we need to setup a power level array. This sensibly starts at
        # 0 kW and in this case we carry it out to the (rounded) overload power level, with a step size of 1 kW.
        powerLevels = np.arange(0, int(self.genOverloadPMax), loadStep)
        # With power level vector setup, we can extract values from the cubic spline of each power level point.
        fuelConsumption = cs(powerLevels)

        # The results are packaged into the fuel curve list, which is the key output of this class.
        self.fuelCurve = list(zip(powerLevels, fuelConsumption))
        # For computational and memory efficiency we also provide a rounded and integer only fuel curve. For this the
        # fuel consumption data points are multiplied by 10,000 and then type cast to integers. The power values are rounded to the nearest
        # kW and type cast to int.
        # NOTE that this variable is significantly more efficient in memory usage.
        self.fuelCurveInt = zip(np.rint(powerLevels).astype(int), np.rint(100000*fuelConsumption).astype(int))