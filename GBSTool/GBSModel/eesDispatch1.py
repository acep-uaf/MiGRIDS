# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class eesDispatch:
    def __init__(self, eess, newP, newQ, newSRC = np.nan):
        """
        Constructor used for intialization of a dispatch scheme.
        :param eess: an energy storage system that is being dispatched
        :param newP: new total power level
        :param newQ: new total reactive power level
        :param newSRC: new spinning reserve requirement. if set to nan, there is no change in the SRC requirement.
        """

        # find the max power available from each generator
        # decide how to split up the requested power between them
        # - simple: proportional to the remaining capacity left in each
        # - use the loss maps to find the least cost. whether diesel generators were used to charge will be considered
        # higher up in a system controller
        # - have indicator to use one for high ramp rate and one for low