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
        # simple calculation, return the mean of the last 5 min load
        self.futureWind = np.mean(prevWindProfile[-300:])