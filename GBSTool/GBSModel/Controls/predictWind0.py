# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 19, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate a short term future Wind power
class predictWind:

    def __init__(self):
        self.futureWind = [0]

    def predictWind(self, SO):
        # prevWindProfile is a list of lists of previous wind power profiles, or a list of estimates of previous wind power
        # simple calculation, return the mean of the last 5 min load
        self.futureWind = []
        #startIdx10min = max(SO.idx - int(600/SO.timeStep),0)
        #startIdx10sec = max(SO.idx - int(10/SO.timeStep),0)
        #stopIdx = SO.idx + 1
        # for each wind turnbine
        for wtg in SO.WF.windTurbines:
            # the future power production is the minimum of the previous 10 min and the previous 10 seconds
            fw10min = wtg.windPower10minTrend[SO.masterIdx]#np.mean(wtg.windPower[startIdx10min:stopIdx])
            fw10sec = wtg.windPower10sTrend[SO.masterIdx] #np.mean(wtg.windPower[startIdx10sec:stopIdx])
            self.futureWind += [min(fw10min,fw10sec)]

