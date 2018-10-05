# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class eesDispatch:
    def runDispatch(self, eess, newP, newQ, newSRC, tIndex):
        """
        Constructor used for intialization of a dispatch scheme.
        :param eess: an energy storage system that is being dispatched
        :param newP: new total power level
        :param newQ: new total reactive power level
        :param newSRC: new spinning reserve requirement. if set to nan, there is no change in the SRC requirement.
        :param tIndex: the index of the current simulation time step.
        """

        # find the max power available from each generator
        # decide how to split up the requested power between them:
        # - simple: proportional to the remaining capacity left in each
        # - use the loss maps to find the least cost. whether diesel generators were used to charge will be considered
        # higher up in a system controller
        # - have indicator to use one for high ramp rate and one for low

        # split power proportionally to remaining power capabilities
        # get power
        if newP > 0: # if discharging
            # get all available powers
            PoutAvail = []
            for ees in eess.electricalEnergyStorageUnits:
                PoutAvail.append(ees.eesPoutAvail)
            # if no power available
            if sum(PoutAvail) <= 0:
                PdisRatio = 0
            else:
                # assign power based on what is available
                PdisRatio = min([newP / sum(PoutAvail), 1])
            # for each electrical energy storage unit in the ees system set a power level and find remaining SRC available
            PsrcAvail = []
            for idx, ees in enumerate(eess.electricalEnergyStorageUnits):
                ees.eesP = PoutAvail[idx]*PdisRatio
                ees.checkOperatingConditions(tIndex)
                PsrcAvail.append(ees.eesPsrcAvail)

        elif newP < 0:  # if discharging
            # get all available powers
            PinAvail = []
            for ees in eess.electricalEnergyStorageUnits:
                PinAvail.append(ees.eesPinAvail)
                # if no power available
            if sum(PinAvail) <= 0:
                PchRatio = 0
            else:
                # assign power based on what is available
                PchRatio = min([-newP / sum(PinAvail), 1])
            # for each electrical energy storage unit in the ees system set a power level and find remaining SRC available
            PsrcAvail = []
            for idx, ees in enumerate(eess.electricalEnergyStorageUnits):
                ees.eesP = -PinAvail[idx] * PchRatio
                ees.checkOperatingConditions(tIndex)
                PsrcAvail.append(ees.eesPsrcAvail)

        else:
            # for each electrical energy storage unit in the ees system set zero power and find remaining SRC available
            PsrcAvail = []
            for idx, ees in enumerate(eess.electricalEnergyStorageUnits):
                ees.eesP = 0
                ees.checkOperatingConditions(tIndex)
                PsrcAvail.append(ees.eesPsrcAvail)

        # assign SRC based on availability
        # if there is no src capability, set to zero
        if sum(PsrcAvail) <= 0 :
            SrcRatio = 0
            # if not energy storage capability of supplying SRC, still distribute SRC to energy storage units. This will
            # force an under SRC flag and initiate the diesel schedule.
            for idx, ees in enumerate(eess.electricalEnergyStorageUnits):
                ees.setSRC(newSRC / len(eess.electricalEnergyStorageUnits))
        else:
            # SrcRatio is not limited to 1, so can over assign SRC, this will lead to underSRC flag being raised.
            SrcRatio = newSRC / sum(PsrcAvail)  # the fraction of available SRC power assigned to each ees
            # set the SRC for each ees and find available remaining power
            for idx, ees in enumerate(eess.electricalEnergyStorageUnits):
                ees.setSRC(PsrcAvail[idx] * SrcRatio)




