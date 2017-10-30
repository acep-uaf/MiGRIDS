# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc.mueller.stoffels@gmail.com
# Date: September 30, 2017 -->
# License: MIT License (see LICENSE file of this package for more information

# This function will eventually return a functional estimate for the power curve of a wind turbine based on data provided
# in 'wtgDescriptor.xml'.
# Currently this is only a place holder since the script was mentioned in documentation.

'''
Description

OBJECTIVE: The fuctionality of this class is to:
    a) determine if the data provide in wtgDescriptor.xml already is sufficiently dense to define the power curve without
    estimation of additional points.
    b) if necessary estimate additional points of the power curve such that a dense curve available.

A dense curve will have power levels associated with all wind speeds in increments of 0.1 m/s and approximates power in
1 kW steps.

ASSUMPTIONS:
    INPUTS: data used as input is already from a cleaned up power curve. This tool is not intended to produce a power
    from operational time-series data, which would require cleaning and filtering. Thus, it is required that for each
    wind speed value one and only one power value exists. That is, temperature compensations, if desired will have to be
    handled separately.

    CUTOUTWINDSPEEDMAX describes the point where the turbine is shut off for protection. Right below this point, it
    produces power at nameplate capacity levels. At this point the turbine is stopped and P = 0 kW.

    CUTOUTWINDSPEEDMIN describes the point where the turbine does not produce power any longer, e.g. P = 0 kW at this
    wind speed.

    CUTINWINDSPEED is the minimum wind speed at which a stopped turbine starts up. At this point power production is
    immediately greater zero, i.e. CUTOUTWINDSPEEDMIN < CUTINWINDSPEED.

METHOD:
    We will use cubic splines to determine a smooth power curve using the data points given, and with the constraints
    described above:
        P(cutOutWindSpeedMin) = 0 kW
        P(cutOutWindSpeedMax) = 0 kW
        P(2*cutOutWindSpeedMax) = 0 kW
        P(cutOutWindSpeedMax-epsilon) = POutMaxPa

    For an algorithm description of cubic splines see here:
    https://en.wikipedia.org/wiki/Spline_(mathematics)#Algorithm_for_computing_natural_cubic_splines

    For a source discussing splines and other methods of estimation see Sohoni, Gupta and Nema, 2016:
    https://www.hindawi.com/journals/jen/2016/8519785/

OUTPUTS:
    The output is a WindPowerCurve object, which contains the new estimated power curve, as well as additional methods
    to estimate air density corrections (later).
'''

# General Imports
import numpy as np
from scipy.interpolate import CubicSpline

'''
The WindPowerCurve class contains methods to determine a wind power curve from data provided in the wtgDescriptor.xml 
file. 
INPUTS: 
    powerCurveDataPoints: list of tuples of floats, e.g., [(ws0, p0), ... , (wsN, pN)], where ws and p are wind speed (m/s) and 
    power (kW) respectively.
    cutInWindSpeed: float, wind speed at which a stopped turbine begins to produce power again, m/s
    cutOutWindSpeedMin: float, the wind speed at which the turbine does not produce power anymore due to lack of wind
    power, units are m/s
    cutOutWindSpeedMax: float, the wind speed at which the turbine is stopped for protection, units are m/s.
    POutMaxPa: float, nameplate power of the turbine, units are kW.

OUTPUTS:
    powerCurve: list of tuples of floats, with a defined range ws = 0 m/s to ws = cutOutWindSpeedMax and some fixed 
    points 
    powerCurve = [(0,0), (cutOutWindSpeedMin, 0), ..., (cutOutWindSpeedMax - 0.1, POutMaxPa), (cutOutWindSpeedMax, 0)]
    Wind speeds are reported in increments of 0.1 m/s, power values are rounded to the next kW. 
'''
class WindPowerCurve:
    # TODO: Testing with sparse data required. Additional checks to be implemented. Documentation


    # ------Variable definitions-------
    # ******Input variables************
    # tuples of wind speed and power, list of tuples of floats, (m/s, kW)
    powerCurveDataPoints = []
    # Cut-in wind speed, float, m/s
    cutInWindSpeed = 0
    # Cut-out wind speed min, float, m/s
    cutOutWindSpeedMin = 0
    # Cut-out wind speed max, float, m/s
    cutOutWindSpeedMax = 0
    # Nameplate power, float, kW
    POutMaxPa = 0

    # ******Internal variables*********
    # Set of coordinates (known points and constraints).
    coords = []

    # ******Output variables***********
    # the power curve, list of tuples of floats, (m/s, kW)
    powerCurve = []
    # the power curve with all entries of type `int`. For this, the wind speeds are multiplied by a factor of 10.
    powerCurveInt = []

    '''
    checkInputs makes sure the input data is self-consistent and setup such that curve estimation methods can be run. 
    This function should be called by all curve estimators. 
    '''
    def checkInputs(self):
        # Check input data is self-consistent
        if not self.powerCurveDataPoints:
            raise ValueError('PowerCurveDataPoints is empty list')
        elif self.cutInWindSpeed == 0 or self.cutOutWindSpeedMin == 0 or self.cutOutWindSpeedMax == 0:
            raise ValueError('Cut-in or cut-out wind speed not initialized with physical value.')
        elif self.cutInWindSpeed < self.cutOutWindSpeedMin or self.cutOutWindSpeedMin > self.cutOutWindSpeedMax:
            raise ValueError('Constraining wind speeds not ordered correctly.')
        elif self.POutMaxPa == 0:
            raise ValueError('Nameplate capacity not initialized.')

        # Setting up the extended data set including constraining tuples
        inptDataPoints = self.powerCurveDataPoints
        inptDataPoints.append((self.cutOutWindSpeedMin, 0))
        inptDataPoints.append((self.cutOutWindSpeedMax, self.POutMaxPa))
        inptDataPoints.append((0, 0))
        # Sort the new list of tuples based on wind speeds.
        inptDataPoints.sort()

        # Check for duplicates and clean up if possible.
        prevVal = (-999, -999)
        for inptDataPoint in inptDataPoints:
            # remove duplicates
            if inptDataPoint[0] == prevVal[0] and inptDataPoint[1] == prevVal[1]:
                inptDataPoints.remove(inptDataPoint)
            # if there's multiple power values for the same wind speed raise an exception
            elif inptDataPoint[0] == prevVal[0] and inptDataPoint[1] != prevVal[1]:
                raise ValueError('Power curve data points  ill-defined, multiple power values for single wind speed.')

            # Copy current to previous value and proceed.
            prevVal = inptDataPoint

        self.coords = inptDataPoints


    '''
    cubicSplineCurveEstimator calculates a cubic spline for the given data points in powerCurveDataPoints using 
    constraints defined by cut-in an cut-out wind speeds. 
    '''
    def cubicSplineCurveEstimator(self):
        self.checkInputs()
        # Setup x and y coordinates as numpy arrays
        x, y = zip(*self.coords)
        xCoords = np.array(x)
        yCoords = np.array(y)

        # Calculate the cubic spline using the scipy function for this. Boundary conditions are that the derivative at
        # end points has to be zero ('clamped'). We do not allow interpolation beyond existing data points. Wind speeds
        # beyond the wind speeds with power data are set to NaN (and subsequently to zero further down).
        cs = CubicSpline(xCoords, yCoords, bc_type='clamped', extrapolate=False)

        # To pull an array of values from the cubic spline, we need to setup a wind speed array. This sensibly starts at
        # 0 m/s and in this case we carry it out to twice the maximum cut-out wind speed, with a step size of 0.1 m/s.
        windSpeeds = np.arange(0, self.cutOutWindSpeedMax*2, 0.1)
        # With wind speed vector setup, we can extract values from the cubic spline of each wind speed point. We
        # immediately backfill the NaNs created by requesting data outside of the initial data range with zeros.
        # NOTE that this assumes that we know that this is true because we have defined values all the way to the
        # cut-out wind speed.
        power = np.nan_to_num(cs(windSpeeds))

        # The results are packaged into the power curve list, which is the key output of this class.
        self.powerCurve = list(zip(windSpeeds, power))
        # For computational and memory efficiency we also provide a rounded and integer only power curve. For this the
        # wind speeds are multiplied by 10 and then type cast to integers. The power values are rounded to the nearest
        # kW and type cast to int.
        # NOTE that this variable is significantly more efficient in memory usage.
        self.powerCurveInt = zip(np.rint(10*windSpeeds).astype(int), np.rint(power).astype(int))








