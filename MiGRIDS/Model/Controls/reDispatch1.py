# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: July 13, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# this object dispatches units with a rule based system. Power setpoints to the wind turbine react slowly to the loading
# on the thermal energy storage system. The TES reacts quickly the the amount of wind power that can be accepted into the
# grid. This requires a TES to be part of the system.
class reDispatch:
    def __init__(self):
        self.wfPimport = 0
        self.rePlimit = 0
        self.wfPch = 0
    def reDispatch(self, SO):
        ## Dispatch units
        # get available wind power
        wfPAvail = sum(SO.WF.wtgPAvail)
        # the maximum amount of power that can be imported from renewable resources
        self.rePlimit = max([SO.P - sum(SO.PH.genMolAvail), 0])
        # amount of imported wind power
        self.wfPimport = min(self.rePlimit, wfPAvail)
        # amount of wind power used to charge the eess is the minimum of maximum charging power and the difference
        # between available wind power and wind power imported to the grid.
        self.wfPch = min(sum(SO.EESS.eesPinAvail), wfPAvail - self.wfPimport)
        # dispatch the wind turbines
        SO.WF.runWtgDispatch(self.wfPimport + self.wfPch, 0, SO.masterIdx)