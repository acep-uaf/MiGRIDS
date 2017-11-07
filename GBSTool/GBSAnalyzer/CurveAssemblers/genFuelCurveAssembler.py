# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc.mueller.stoffels@gmail.com
# Date: September 30, 2017 -->
# License: MIT License (see LICENSE file of this package for more information)

'''
This module contains methods to build a dense fuel curve for diesel generators based on sparser information provided in
`genDescriptor.xml`.  There the fuel curve contains tuples of tags, pPu (power in P.U. referenced to nameplate capacity)
and massFlow in kg/s. Here the intent is to provide a density of points such that there is a fuel consumption data point
for each 1 kW increment in power level. For practical reasons, the pPu output curve does include overload values, which
exhibit the same fuel consumption as the largest data point actually given.

'''

# *** General Imports ***
from scipy.interpolate import CubicSpline
import numpy as np

'''
GenFuelCurve class description
'''

class GenFuelCurve:
    # ******* INPUT VARIABLES *******

    # ******* INTERNAL VARIABLES *******

    # ******* OUTPUT VARIABLES *******


