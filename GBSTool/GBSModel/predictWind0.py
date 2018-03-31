# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 19, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate a short term future Wind power
class predictWind:

    def __init__(self):
        self.futureWind = 0

    def predictWind(self, prevWindProfile,time):
        # prevWindProfile is a list of lists of previous wind power profiles, or a list of estimates of previous wind power
        # simple calculation, return the mean of the last 5 min load
        futureWind = []
        for wp in prevWindProfile:
            if isinstance(wp,(list,tuple,np.ndarray)):
                futureWind += np.mean(wp[-300:])
            else:
                futureWind += [wp]
        self.futureWind = futureWind