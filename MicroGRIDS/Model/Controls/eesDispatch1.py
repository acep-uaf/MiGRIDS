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
        # This charges and discharges the ees in the order they are numbered. So ees0 with be discharged first and
        # charge first. This is to simulate the scenario where ees0 is a high power (eg ultra caps or flywheel) that can
        # handle many cycles. ees1 and above are more energy focussed and should not be cycled as much.

        # split power proportionally to remaining power capabilities
        # get power
        if newP > 0: # if discharging
            # for each electrical energy storage unit in the ees system set a power level and find remaining SRC available
            PsrcAvail = []
            newPremaining = newP # the remaining power after the scheduling previous ees
            for ees in eess.electricalEnergyStorageUnits:
                ees.eesP = min(ees.eesPoutAvail,newPremaining)
                newPremaining = newPremaining - ees.eesP
                ees.checkOperatingConditions(tIndex)
                PsrcAvail.append(ees.eesPsrcAvail)

        elif newP < 0:  # if discharging
            # for each electrical energy storage unit in the ees system set a power level and find remaining SRC available
            PsrcAvail = []
            newPremaining = newP  # the remaining power after the scheduling previous ees
            for ees in eess.electricalEnergyStorageUnits:
                ees.eesP = max(-ees.eesPinAvail, newPremaining)
                newPremaining = newPremaining + ees.eesP
                ees.checkOperatingConditions(tIndex)
                PsrcAvail.append(ees.eesPsrcAvail)

        else:
            # for each electrical energy storage unit in the ees system set zero power and find remaining SRC available
            PsrcAvail = []
            for ees in eess.electricalEnergyStorageUnits:
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




