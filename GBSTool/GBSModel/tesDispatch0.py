# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class eesDispatch:
    def __init__(self, tess, newP):
        """
        Constructor used for intialization of a dispatch scheme.
        :param eess: an energy storage system that is being dispatched
        :param newP: new total power level
        :param newQ: new total reactive power level
        :param newSRC: new spinning reserve requirement. if set to nan, there is no change in the SRC requirement.
        """





