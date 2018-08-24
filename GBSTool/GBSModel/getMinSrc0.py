# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 3, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate the minimum required src

class getMinSrc:

    def __init__(self, args):
        self.minSRCToSwitchRatio = args['minSRCToSwitchRatio']
        self.minSrcToStay = 0
        self.minSrcToSwitch = 0

    def getMinSrc(self, SO, calcFuture = False):

        # Take the average load of this hour last week 24.5hr * 3600 s/hr = 617400s , 23.5hr * 3600 = 592200
        # try with and without, compare the difference in performance.
        #meanLastWeek = np.mean(prevLoad[int(-617400/timeStep):int(-592200/timeStep)])
        # if a list is given for prevLoad, get mean value, otherwise, use the value given

        if calcFuture:
            # the minimum src required.
            # remove non firm power from the SRC requirements
            self.minSrcToStay = SO.futureLoad * SO.DM.minSRC + sum([a * b for a, b in zip(SO.futureWind, SO.WF.wtgMinSrcCover)])  # catch zero instances of wind power with max statement. in this case, nonFirmWtgP will be 0 as well.
            # when scheduling new units online, use a higher SRC in order to avoid having just enough power to cover SRC required
            # and then have the requirement increase
            self.minSrcToSwitch = self.minSrcToStay * self.minSRCToSwitchRatio
        else:

            meanLastTenMin = SO.DM.realLoad10minTrend[SO.idx] #np.mean(SO.DM.realLoad[max((SO.idx - int(600/SO.timeStep)), 0):(SO.idx+1)])

            # the minimum src required.
            # remove non firm power from the SRC requirements
            if hasattr(SO,'TESS'):
                nonFirmWtgP = SO.reDispatch.wfPch + sum(SO.TESS.tesP)
            else:
                nonFirmWtgP = SO.reDispatch.wfPch
            self.minSrcToStay = meanLastTenMin*SO.DM.minSRC + sum([a*b for a,b in zip(SO.WF.wtgP,SO.WF.wtgMinSrcCover)])*(1 - nonFirmWtgP/max(sum(SO.WF.wtgP),1)) # catch zero instances of wind power with max statement. in this case, nonFirmWtgP will be 0 as well.
            # when scheduling new units online, use a higher SRC in order to avoid having just enough power to cover SRC required
            # and then have the requirement increase
            self.minSrcToSwitch = self.minSrcToStay*self.minSRCToSwitchRatio
