# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class tesDispatch:
    def __init__(self):
        """
        Constructor used for intialization of a dispatch scheme.
        :param eess: an energy storage system that is being dispatched
        :param newP: new total power level
        :param newQ: new total reactive power level
        :param newSRC: new spinning reserve requirement. if set to nan, there is no change in the SRC requirement.
        """
    def tesDispatch(self, TESS, P):
        loadingP = np.nanmin([np.nanmax([P / np.sum(TESS.tesPAvail), 0]), 1])
        TESS.tesP = [P / len(TESS.tesP)] * len(TESS.tesP)
        for idx in range(len(TESS.tesP)):
            TESS.thermalEnergyStorageUnits[idx].tesP = loadingP * TESS.tesPAvail[idx]




