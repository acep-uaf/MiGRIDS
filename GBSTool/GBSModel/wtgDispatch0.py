
# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: October 2, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class wtgDispatch:
    def runDispatch(self,wf, newWtgP, newWtgQ = 0):
        """
        Proportional loading of wind turbines, based on power available.
        :param wf: wind farm object
        :param newWtgP: new wind power setpoint
        :param newWtgQ: new reactive wind power setpoint
        :return: none
        """
        # get the loading pu for real and reactive power
        wtgPAvailTot = sum(wf.wtgPAvail)
        if wtgPAvailTot == 0:
            loadingP = 0
        else:
            loadingP = min([max([newWtgP / wtgPAvailTot, 0]), 1])  # this is the PU loading of each wtg, limited to 1

        wtgQAvailTot = sum(wf.wtgQAvail)
        if wtgQAvailTot == 0:
            loadingQ = 0
        else:
            loadingQ = min([max([newWtgQ / wtgQAvailTot, 0]), 1])  # this is the PU loading of each wtg
        # cycle through each wtg and update with new P and Q
        for idx in range(len(wf.wtgIDS)):
            wf.windTurbines[idx].wtgP = loadingP * wf.wtgPAvail[idx]
            wf.windTurbines[idx].wtgQ = loadingQ * wf.wtgQAvail[idx]
            # update the local variable that keeps track of wtg power
            wf.wtgP[idx] = wf.windTurbines[idx].wtgP
            wf.wtgQ[idx] = wf.windTurbines[idx].wtgQ






