
# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: October 1, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class genSchedule:
    def __init__(self,args):
        # whether to try to minimize fuel consumption or maximize RE contribution (by minimizing MOL of generators)
        self.minimizeFuel = args['minimizeFuel']
    def runSchedule(self, ph, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay, underSRC):
        # scheduled load is the difference between load and RE, the min of what needs to be provided by gen or ess
        scheduledLoad = max(futureLoad - futureRE,0)

        ## first find all generator combinations that can supply the load within their operating bounds
        # find all with capacity over the load and the required SRC
        capReq = max(int(scheduledLoad - powerAvailToSwitch + scheduledSRCSwitch),0)
        indCap = np.asarray(ph.lkpGenCombinationsUpperNormalLoading.get(capReq, ph.genCombinationsUpperNormalLoadingMaxIdx), dtype=int)

        # check if the current online combination is capable of supplying the projected load minus the power available to
        # help the current generator combination stay online
        if ph.onlineCombinationID not in indCap and not (True in ph.outOfNormalBounds) and not underSRC: # keep current generating combingation in the mix unless has gone out of bounds for allotted amount
                        #ph.genCombinationsUpperNormalLoading[ph.onlineCombinationID] >= scheduledLoad + scheduledSRCStay - powerAvailToStay:
            # do not add the current generating option if it is diesel-off and it does not have enough SRC
            #if not((ph.onlineCombinationID == 0) and underSRC):
                indCap = np.append(indCap,ph.onlineCombinationID)
        # if there are no gen combinations large enough to supply, automatically add largest (last combination)
        if indCap.size == 0:
            indCap = np.append(indCap,len(ph.genCombinationsUpperNormalLoading)-1)
            indInBounds = indCap

        elif indCap.size == 1:
            indInBounds = indCap

        else:
            # find all with MOL under the load
            indMOLCap = [idx for idx, x in enumerate(ph.genCombinationsMOL[indCap]) if x <= futureLoad]
            # ind of in bounds combinations
            indInBounds = indCap[indMOLCap]

        # if there are no gen combinations with a low enough MOL enough to supply, automatically add combination 1,
        # which is to smallest generator combination without turning off the generators
        if indInBounds.size == 0:
            indInBounds = np.array([indCap[0]])

        indInBounds = np.atleast_1d(indInBounds)

        ## then check how long it will take to switch to any of the combinations online
        lenGenerators = len(ph.generators)
        turnOnTime = [None]*lenGenerators
        turnOffTime = [None]*lenGenerators
        for idx, gen in enumerate(ph.generators):
            # get the time remaining to turn on each generator
            # include this time step in the calculation. this avoids having to wait 1 time step longer than necessary to bring a diesel generator online.
            turnOnTime[idx] = gen.genStartTime - gen.genStartTimeAct - ph.timeStep
            # get the time remaining to turn off each generator
            turnOffTime[idx] = gen.genRunTimeMin - gen.genRunTimeAct - ph.timeStep

        # Go through each potential combination of generators and find which generators need to be switched on and
        # offline for each combination
        lenIndInBounds = indInBounds.size #len(indInBounds)
        genSwOn = [] # the generators to be switched on for each possible combination
        genSwOff = [] # the generators to be switched off for each possible combination
        timeToSwitch = [None]*lenIndInBounds # the time switch for each in bounds generator combination
        fuelCons = [None]*lenIndInBounds # the predicted fuel consumption for each combination
        for ind, idx in enumerate(np.atleast_1d(indInBounds)): # for each combination that is in bounds
            # inititiate the generators to be switched on for this combination to all generators in the combination
            genSwOn.append(list(ph.genCombinationsID[idx]))
            # initiate the generators to be switched off for this combination to all generators currently online
            genSwOff.append(list(ph.genCombinationsID[ph.combinationsID.index(ph.onlineCombinationID)]))
            # find common elements between switch on and switch off lists
            commonGen = list(set(genSwOff[-1]).intersection(genSwOn[-1]))
            # remove common generators from both lists
            for genID in commonGen:
                genSwOn[-1].remove(genID)
                genSwOff[-1].remove(genID)
            # for each gen to be switched get time, max time for combination is time will take to bring online

            # find max time to switch generators online
            onTime = 0
            for genID in genSwOn[-1]: # for each to be brought online in the current combination
                onTime = max(onTime,turnOnTime[ph.genIDS.index(genID)]) # max turn on time
            # find max of turn on time and turn off time
            SwitchTime = onTime # initiate to max turn on time
            for genID in genSwOff[-1]: # for each generator to be switched off in the current combination
                SwitchTime = max(SwitchTime, turnOffTime[ph.genIDS.index(genID)]) # check if there is a higher turn off time
            timeToSwitch[ind] = SwitchTime

            if self.minimizeFuel:
                # get the generator fuel consumption at this loading for this combination
                FCpower, FCcons = zip(*ph.genCombinationsFCurve[idx]) # separate out the consumptio n and power
                # check if this is the online combination. If so, use the power available to stay online to calculate the
                # the load required by the generator
                if idx == ph.onlineCombinationID:
                    useScheduledLoad = int(max([scheduledLoad - powerAvailToStay, ph.genCombinationsMOL[idx]]))
                else:
                    useScheduledLoad = int(max([scheduledLoad - powerAvailToSwitch, ph.genCombinationsMOL[idx]]))
                indFCcons = getIntListIndex(useScheduledLoad, FCpower)

                fuelCons[ind] = FCcons[indFCcons]
                # TODO: Add cost of switching generators



        ## bring the best option that can be switched immediatley, if any
        # if the most efficient option can't be switched, start warming up generators
        # order fuel consumptions
        if self.minimizeFuel:
            indSort = np.argsort(fuelCons)
        else:
            indSort = np.argsort(ph.genCombinationsMOL[indInBounds])

        # if the most efficient can be switched on now, switch to it
        if timeToSwitch[indSort[0]] <= 0:
            # update online generator combination
            ph.onlineCombinationID = ph.combinationsID[indInBounds[indSort[0]]]
            ph.switchGenComb(genSwOn[indSort[0]], genSwOff[indSort[0]])  # switch generators
            for idx in range(len(ph.genIDS)):
                # update genPAvail
                ph.generators[idx].updateGenPAvail()
        # otherwise, start or continue warming up generators for most efficient combination
        else:
            ph.startGenComb(genSwOn[indSort[0]])
            # otherwise, if a generator is out of bounds (not just normal bounds) switch to the best possible, if can
            if (True in (np.array(timeToSwitch)<=0)) & (True in ph.outOfBounds):
                # find most efficient option that can be switched now
                indBest = next((x for x in range(len(indSort)) if timeToSwitch[indSort[x]] <= 0 )) # indBest wrt indSort
                # update online generator combination
                ph.onlineCombinationID = ph.combinationsID[indInBounds[indSort[indBest]]]
                ph.switchGenComb(genSwOn[indSort[indBest]],genSwOff[indSort[indBest]]) # switch generators
                for idx in range(len(ph.genIDS)):
                    # update genPAvail
                    ph.generators[idx].updateGenPAvail()