# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import itertools
import sys

import numpy as np

from GBSModel.Generator import Generator

sys.path.append('../')
from GBSAnalyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve
from GBSModel.getIntListIndex import getIntListIndex


# import GeneratorDispatch

class Powerhouse:
    # __init()__ Class constructor. Initiates the setup of the individual generators as per the initial input.
    # Inputs:
    # self - self reference, always required in constructor
    # genIDS - list of generator IDs, which should be integers
    # genP - list of generator real power levels for respective generators listed in genIDS
    # genQ - list of generator reactive power levels for respective generators listed in genIDS
    # genDescriptor - list of generator descriptor XML files for the respective generators listed in genIDS, this should
    #   be a string with a relative path and file name, e.g., /InputData/Components/gen1Descriptor.xml
    def __init__(self, genIDS, genStates, timeStep, genDescriptor):
        # check to make sure same length data coming in
        if not len(genIDS)==len(genStates):
            raise ValueError('The length genIDS, genP, genQ and genStates inputs to Powerhouse must be equal.')
        # ************Powerhouse variables**********************
        # List of generators and their respective IDs
        self.generators = []
        self.genIDS = genIDS

        # total capacities
        self.genPMax = 0
        self.genQMax = 0

        # Generator dispatch object
        self.genDispatchType = 1  # generator dispatch to use, 1 for proportional
        self.outOfNormalBounds = []
        self.outOfBounds = []
        self.genMol = []
        self.genUpperNormalLoading = []
        self.genUpperLimit = []
        self.genLowerLimit = []

        # Cumulative operational data
        # Actual loadings
        self.genP = []
        self.genQ = []
        # Total available gen power without new dispatch
        self.genPAvail = []
        self.genQAvail = []

        # the minimum power output based on MOL
        self.genMolAvail = []
        """

        :param genIDS:
        :param genP:
        :param genQ:
        :param genDescriptor:
        """

        # Populate the list of generators with generator objects
        for idx, genID in enumerate(genIDS):
            # Initialize generators
            self.generators.append(Generator(genID, genStates[idx], timeStep, genDescriptor[idx]))

            # Initial value for genP, genQ, genPAvail and genQAvail can be handled while were in this loop
            self.genPMax = self.genPMax + self.generators[idx].genPMax
            self.genQMax = self.genQMax + self.generators[idx].genQMax
            self.genP += [self.generators[idx].genP]
            self.genQ += [self.generators[idx].genQ]
            self.genPAvail += [self.generators[idx].genPAvail]
            self.genQAvail += [self.generators[idx].genQAvail]
            self.genMolAvail += [self.generators[idx].genMolAvail]
            self.outOfNormalBounds.append(self.generators[idx].outOfNormalBounds)
            self.outOfBounds.append(self.generators[idx].outOfBounds)
            self.genMol.append(self.generators[idx].genMol) # the MOLs of each generator
            self.genUpperNormalLoading.append(self.generators[idx].genUpperNormalLoading)  # the genUpperNormalLoading of each generator
            self.genUpperLimit.append(self.generators[idx].genUpperLimit) # the upper limit of each generator
            self.genLowerLimit.append(self.generators[idx].genLowerLimit) # the lower limit of each generator

        # Create a list of all possible generator combination ID, MOL, upper normal loading, upper limit and lower limit
        # these will be used to schedule the diesel generators
        self.combinationsID = range(2**len(self.genIDS)) # the IDs of the generator combinations
        self.genCombinationsID = [] # the gen IDs in each combination
        self.genCombinationsMOL = np.array([])
        self.genCombinationsUpperNormalLoading = []
        self.genCombinationsUpperLimit = []
        self.genCombinationsLowerLimit = []
        self.genCombinationsPMax = []
        self.genCombinationsFCurve = []
        self.genMaxDiesCapCharge = []
        for nGen in range(len(self.genIDS)+1): # for all possible numbers of generators
            for subset in itertools.combinations(self.genIDS, nGen): # get all possible combinations with that number
                self.genCombinationsID.append(subset) # list of lists of gen IDs
                # get the minimum normal loading (if all operating at their MOL)
                subsetMOLPU = 0
                subsetGenUpperNormalLoading = 0 # the normal upper loading
                subsetGenUpperLimit = 0
                subsetGenLowerLimit = 0
                subsetPMax = 0
                powerLevelsPU = [] # pu power levels in combined fuel curve for combination
                fuelConsumption = [] # fuel consumption for combined fuel curve
                for gen in subset: # for each generator in the combination
                    subsetPMax += self.generators[self.genIDS.index(gen)].genPMax
                    subsetMOLPU = max(subsetMOLPU,self.genMol[self.genIDS.index(gen)]/self.generators[self.genIDS.index(gen)].genPMax) # get the max pu MOL of the generators
                    subsetGenUpperNormalLoading += self.genUpperNormalLoading[self.genIDS.index(gen)]
                    subsetGenUpperLimit += self.genUpperLimit[self.genIDS.index(gen)]
                    subsetGenLowerLimit += self.genLowerLimit[self.genIDS.index(gen)]

                self.genCombinationsMOL = np.append(self.genCombinationsMOL, subsetMOLPU*subsetPMax) # pu MOL * P max =  MOL
                self.genCombinationsUpperNormalLoading.append(subsetGenUpperNormalLoading)
                self.genCombinationsUpperLimit.append(subsetGenUpperLimit)
                self.genCombinationsLowerLimit.append(subsetGenLowerLimit)
                self.genCombinationsPMax.append(subsetPMax)
                self.genCombinationsFCurve.append(self.combFuelCurves(subset)) # append fuel curve for this combination
                self.genMaxDiesCapCharge.append(self.combMaxDiesCapCharge(subset)) # append the max diesel cap charge values for this combination

        # Update the current combination online
        for idx, combID in enumerate(self.combinationsID): # for each combination
            # get the gen IDs of online generators
            onlineGens = [genIDS[idx] for idx, x in enumerate(genStates) if x == 2]
            # if the gen IDs of this combination equal the gen IDs that are currently online, then this is current online combination
            if sorted(self.genCombinationsID[idx]) == sorted(onlineGens):
                self.onlineCombinationID = combID


    # combine fuel curves for a combination of generators
    # self - self reference
    # generators - a list of generator objects in the combination
    # combPMax - the name plate capacity of the combination of generators
    def combFuelCurves(self, genIDs):
        # get the max power of the combination
        combPMax = 0 # initiate to zero
        combFuelPower = [0]
        combFuelConsumption = [0]
        for genID in genIDs:
            combPMax += int(self.generators[self.genIDS.index(genID)].genPMax) # add each generator max power

        combFuelConsumption = np.array([0.0]*combPMax) # initiate fuel consumption array
        combFuelPower = list(range(combPMax)) # list of the powers corresponding to fuel consumption

        # for each generator, resample the fuel curve to get the desired loading levels
        for genID in genIDs:
            powerStep = self.generators[self.genIDS.index(genID)].genPMax / combPMax # the required power step in the fuel curve to get 1 kW steps in combined fuel curve
            genFC = GenFuelCurve() # initiate fuel curve object
            genFC.fuelCurveDataPoints = self.generators[self.genIDS.index(genID)].genFuelCurve # populate with generator fuel curve points
            genFC.genOverloadPMax = self.generators[self.genIDS.index(genID)].genPMax # set the max power to the nameplate capacity
            genFC.cubicSplineCurveEstimator(powerStep) # calculate new fuel curve
            combFuelConsumption += np.array([y for x, y in genFC.fuelCurve]) # add the fuel consumption for each generator

        if len(combFuelPower) == 0:
            combFuelPower = [0]
            combFuelConsumption = [0]

        return list(zip(combFuelPower, list(combFuelConsumption))) # return list of tuples

    # combine max diesel cap charging of ESS for a combination of generators
    # self - self reference
    # genIDs - a list of generator objects in the combination
    # returns a list of tuples (Diesel Max Loading, EESS max state of charge)
    def combMaxDiesCapCharge(self, genIDs):
        # for each genID, take the average of maxDiesCapCharge and maxDiesCapChargeE
         for idx, genID in enumerate(genIDs):
             if idx == 0:
                 gmdcce, gmdcc = zip(*self.generators[self.genIDS.index(genID)].maxDiesCapCharge)
             else:
                 gmdcce0, gmdcc0 = zip(*self.generators[self.genIDS.index(genID)].maxDiesCapCharge)
                 gmdcc = list((np.array(gmdcc) + np.array(gmdcc0)) / 2)
                 gmdcce = list((np.array(gmdcce) + np.array(gmdcce0)) / 2)
         if len(genIDs) == 0: # for diesel-off scenario
             gmdcc = [0]
             gmdcce = [0]
         return list(zip(gmdcce, gmdcc))

    # genDispatch class method. Assigns a loading to each online generator and checks if they are inside operating bounds.
    # Inputs:
    # self - self reference
    # newGenP - new total generator real load
    # newGenQ - new total generator reactive load
    def genDispatch(self, newGenP, newGenQ):
        # dispatch
        if self.genDispatchType == 1: # if proportional loading
            # make sure to update genPAvail and genQAvail before
            # check if no diesel generators online. still assign power, this will be flagged as a power outage
            if sum(self.genPAvail)==0:
                for idx in range(len(self.genIDS)):
                    self.generators[idx].genP = newGenP/len(self.genIDS)
                    self.generators[idx].genQ = newGenQ/len(self.genIDS)
                    # update the local variable that keeps track of generator power
                    self.genP[idx] = self.generators[idx].genP
                    self.genQ[idx] = self.generators[idx].genQ
            else:
                loadingP = newGenP / max(np.sum(self.genPAvail),1) # this is the PU loading of each generator. max with 1 for 0 capacity instance
                loadingQ = newGenQ / max(np.sum(self.genQAvail),1)  # this is the PU loading of each generator
                # cycle through each gen and update with new P and Q
                for idx in range(len(self.genIDS)):
                    self.generators[idx].genP = loadingP * self.generators[idx].genPAvail
                    self.generators[idx].genQ = loadingQ * self.generators[idx].genQAvail
                    # update the local variable that keeps track of generator power
                    self.genP[idx] = self.generators[idx].genP
                    self.genQ[idx] = self.generators[idx].genQ
        else:
            print('The generator dispatch is not supported. ')

        # check operating bounds for each generator
        for idx in range(len(self.genIDS)):
            self.generators[idx].checkOperatingConditions()
            # check if out of bounds
            self.outOfNormalBounds[idx] = self.generators[idx].outOfNormalBounds
            self.outOfBounds[idx] = self.generators[idx].outOfBounds
            # get available power and minimum loading from each
            self.genPAvail[idx] = self.generators[idx].genPAvail
            self.genQAvail[idx] = self.generators[idx].genQAvail
            self.genMolAvail[idx] = self.generators[idx].genMolAvail
            # get the spinning reserve being supplied by the generators
            #self.genSRC[idx] = self.generators[idx].genPAvail - self.generators[idx].genP

        # manage generators that are warming up. If have run for 2x start up time, shut them off.
        # TODO: remove hard coded 2x and place as value in descriptor file and Generator class
        for gen in self.generators:
            # get the time remaining to turn on each generator
            # if greater than 2 times the required start time, it was likely started but is no longer needed
            if gen.genStartTimeAct > gen.genStartTime * 2:
                if gen.genState == 1: # only switch off if not running online
                    gen.genState = 0



    # genSchedule class method. Brings another generator combination online
    # Inputs:
    # self - self reference
    # scheduledLoad - the load that the generators will be expected to supply, this is predicted based on previous loading
    # scheduledSRC -  the minimum spinning reserve that the generators will be expected to supply
    # schedWithFuelCons -  minimize fuel consumption in the scheduling of generators. If false, it will schedule the combination with the lowest MOL
    def genSchedule(self, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay,underSRC, minimizeFuel = False):

        # scheduled load is the difference between load and RE, the min of what needs to be provided by gen or ess
        scheduledLoad = max([futureLoad - futureRE])

        ## first find all generator combinations that can supply the load within their operating bounds
        # find all with capacity over the load and the required SRC
        indCap = np.array([idx for idx, x in enumerate(self.genCombinationsUpperNormalLoading) if x >= scheduledLoad -
                           powerAvailToSwitch + scheduledSRCSwitch])
        # check if the current online combination is capable of supplying the projected load minus the power available to
        # help the current generator combination stay online
        if self.onlineCombinationID not in indCap and not any(self.outOfNormalBounds) and not underSRC: # keep current generating combingation in the mix unless has gone out of bounds for allotted amount
                        #self.genCombinationsUpperNormalLoading[self.onlineCombinationID] >= scheduledLoad + scheduledSRCStay - powerAvailToStay:
            # do not add the current generating option if it is diesel-off and it does not have enough SRC
            #if not((self.onlineCombinationID == 0) and underSRC):
                indCap = np.append(indCap,self.onlineCombinationID)
        # if there are no gen combinations large enough to supply, automatically add largest (last combination)
        if len(indCap) == 0:
            indCap = np.array([len(self.genCombinationsUpperNormalLoading)-1])
        # find all with MOL under the load
        indMOLCap = [idx for idx, x in enumerate(self.genCombinationsMOL[indCap]) if x <= futureLoad]
        # ind of in bounds combinations
        indInBounds = indCap[indMOLCap]
        # if there are no gen combinations with a low enough MOL enough to supply, automatically add combination 1,
        # which is to smallest generator combination without turning off the generators
        if len(indInBounds) == 0:
            indInBounds = np.array([indCap[0]])

        ## then check how long it will take to switch to any of the combinations online
        turnOnTime = []
        turnOffTime = []
        for gen in self.generators:
            # get the time remaining to turn on each generator
            turnOnTime.append(gen.genStartTime - gen.genStartTimeAct)
            # get the time remaining to turn off each generator
            turnOffTime.append(gen.genRunTimeMin - gen.genRunTimeAct)

        # Go through each potential combination of generators and find which generators need to be switched on and
        # offline for each combination
        genSwOn = [] # the generators to be switched on for each possible combination
        genSwOff = [] # the generators to be switched off for each possible combination
        timeToSwitch = [] # the time switch for each in bounds generator combination
        fuelCons = [] # the predicted fuel consumption for each combination
        for idx in indInBounds: # for each combination that is in bounds
            # inititiate the generators to be switched on for this combination to all generators in the combination
            genSwOn.append(list(self.genCombinationsID[idx]))
            # initiate the generators to be switched off for this combination to all generators currently online
            genSwOff.append(list(self.genCombinationsID[self.combinationsID.index(self.onlineCombinationID)]))
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
                onTime = max(onTime,turnOnTime[self.genIDS.index(genID)]) # max turn on time
            # find max of turn on time and turn off time
            SwitchTime = onTime # initiate to max turn on time
            for genID in genSwOff[-1]: # for each generator to be switched off in the current combination
                SwitchTime = max(SwitchTime, turnOffTime[self.genIDS.index(genID)]) # check if there is a higher turn off time
            timeToSwitch.append(SwitchTime)

            if minimizeFuel:
                # get the generator fuel consumption at this loading for this combination
                FCpower, FCcons = zip(*self.genCombinationsFCurve[idx]) # separate out the consumptio n and power
                # check if this is the online combination. If so, use the power available to stay online to calculate the
                # the load required by the generator
                if idx == self.onlineCombinationID:
                    useScheduledLoad = int(max([scheduledLoad - powerAvailToStay, self.genCombinationsMOL[idx]]))
                else:
                    useScheduledLoad = int(max([scheduledLoad - powerAvailToSwitch, self.genCombinationsMOL[idx]]))
                indFCcons = getIntListIndex(useScheduledLoad,FCpower)

                fuelCons.append(FCcons[indFCcons])
                # TODO: Add cost of switching generators



        ## bring the best option that can be switched immediatley, if any
        # if the most efficient option can't be switched, start warming up generators
        # order fuel consumptions
        if minimizeFuel:
            indSort = np.argsort(fuelCons)
        else:
            indSort = np.argsort(self.genCombinationsMOL[indInBounds])

        # if the most efficient can be switched on now, switch to it
        if timeToSwitch[indSort[0]] <= 0:
            # update online generator combination
            self.onlineCombinationID = self.combinationsID[indInBounds[indSort[0]]]
            self.switchGenComb(genSwOn[indSort[0]], genSwOff[indSort[0]])  # switch generators
            for idx in range(len(self.genIDS)):
                # update genPAvail
                self.generators[idx].checkOperatingConditions()
        # otherwise, start or continue warming up generators for most efficient combination
        else:
            self.startGenComb(genSwOn[indSort[0]])
            # otherwise, if a generator is out of bounds (not just normal bounds) switch to the best possible, if can
            if (True in (np.array(timeToSwitch)<=0)) & (True in self.outOfBounds):
                # find most efficient option that can be switched now
                indBest = next((x for x in range(len(indSort)) if timeToSwitch[indSort[x]] <= 0 )) # indBest wrt indSort
                # update online generator combination
                self.onlineCombinationID = self.combinationsID[indInBounds[indSort[indBest]]]
                self.switchGenComb(genSwOn[indSort[indBest]],genSwOff[indSort[indBest]]) # switch generators



    # switch generators on and off
    def switchGenComb(self,GenSwOn, GenSwOff):
        # bring online
        for genID in GenSwOn:
            self.generators[self.genIDS.index(genID)].genState = 2 # switch online
        # turn off
        for genID in GenSwOff:
            self.generators[self.genIDS.index(genID)].genState = 0  # switch offline

            # switch generators on and off
    def startGenComb(self, GenSwOn):
        # start the gennerators
        for genID in GenSwOn:
            self.generators[self.genIDS.index(genID)].genState = 1  # running but offline
