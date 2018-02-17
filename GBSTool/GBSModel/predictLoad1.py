# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate a short term future load
class predictLoad:

    def __init__(self):
        self.futureLoad = 0

    def predictLoad(self, prevLoadProfile,time):
        # simple calculation, return the mean of the last 5 min load
        self.futureLoad = np.mean(prevLoadProfile[-300:])