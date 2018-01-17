# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import Generator
import itertools
import sys
import numpy as np
sys.path.append('../')
from GBSAnalyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve

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
    def __init__(self, genIDS, genP, genQ, genStates, timeStep, genDescriptor):
        # check to make sure same length data coming in
        if not len(genIDS)==len(genP)==len(genQ)==len(genStates):
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
        self.outOfBounds = []
        self.genMol = []
        self.genUpperNormalLoading = []
        self.genUpperLimit = []
        self.genLowerLimit = []

        # Cumulative operational data
        # Actual loadings
        self.genP = 0
        self.genQ = 0
        # Total available gen power without new dispatch
        self.genPAvail = 0
        self.genQAvail = 0
        """

        :param genIDS:
        :param genP:
        :param genQ:
        :param genDescriptor:
        """

        # Populate the list of generators with generator objects
        for idx, genID in enumerate(genIDS):
            # Initialize generators
            self.generators.append(self, Generator(genID, genP[idx], genQ[idx], genStates[idx], timeStep, genDescriptor[idx]))

            # Initial value for genP, genQ, genPAvail and genQAvail can be handled while were in this loop
            self.genPMax = self.genPMax + self.generators[idx].genPMax
            self.genQMax = self.genQMax + self.generators[idx].genQMax
            self.genP = self.genP + self.generators[idx].genP
            self.genQ = self.genQ + self.generators[idx].genQ
            self.genPAvail = self.genPAvail + self.generators[idx].genPAvail
            self.genQAvail = self.genQAvail + self.generators[idx].genQAvail
            self.outOfBounds.append(self.generators[idx].outOfBounds)
            self.genMol.append(self.generators[idx].genMol) # the MOLs of each generator
            self.genUpperNormalLoading.append(self.generators[idx].genUpperNormalLoading)  # the genUpperNormalLoading of each generator
            self.genUpperLimit.append(self.generators[idx].genUpperLimit) # the upper limit of each generator
            self.genLowerLimit.append(self.generators[idx].genLowerLimit) # the lower limit of each generator

        # Create a list of all possible generator combination ID, MOL, upper normal loading, upper limit and lower limit
        # these will be used to schedule the diesel generators
        self.combinationsID = range(2^len(self.genIDS)-1) # the IDs of the generator combinations
        self.genCombinationsID = [] # the gen IDs in each combination
        self.genCombinationsMOL = []
        self.genCombinationsUpperNormalLoading = []
        self.genCombinationsUpperLimit = []
        self.genCombinationsLowerLimit = []
        self.genCombinationsPMax = []
        self.genCombinationsFCurve = []
        for nGen in range(self.genIDS): # for all possible numbers of generators
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

                self.genCombinationsMOL.append(subsetMOLPU*subsetPMax) # pu MOL * P max =  MOL
                self.genCombinationsUpperNormalLoading.append(subsetGenUpperNormalLoading)
                self.genCombinationsUpperLimit.append(subsetGenUpperLimit)
                self.genCombinationsLowerLimit.append(subsetGenLowerLimit)
                self.genCombinationsPMax.append(subsetPMax)
                self.genCombinationsFCurve.append(self.combFuelCurves(subset)) # append fuel curve for this combination

        # Update the current combination online
        for idx, combID in enumerate(self.combinationsID): # for each combination
            # get the gen IDs of online generators
            onlineGens = [genIDS[idx] for idx, x in enumerate(genStates) if x == 2]
            # if the gen IDs of this combination equal the gen IDs that are currently online, then this is current online combination
            if sorted(self.genCombinationsID[idx]) == sorted(onlineGens):
                self.genCombinationOnline = combID


    # combine fuel curves for a combination of generators
    # self - self reference
    # generators - a list of generator objects in the combination
    # combPMax - the name plate capacity of the combination of generators
    def combFuelCurves(self, generators):
        # get the max power of the combination
        combPMax = 0 # initiate to zero
        for gen in generators:
            combPMax += int(gen.genPMax) # add each generator max power

        combFuelConsumption = np.array([0]*combPMax) # initiate fuel consumption array
        combFuelPower = list(range(combPMax)) # list of the powers corresponding to fuel consumption

        # for each generator, resample the fuel curve to get the desired loading levels
        for gen in generators:
            powerStep = gen.genPMax / combPMax # the required power step in the fuel curve to get 1 kW steps in combined fuel curve
            genFC = GenFuelCurve() # initiate fuel curve object
            genFC.fuelCurveDataPoints = gen.genFuelCurve # populate with generator fuel curve points
            genFC.genOverloadPMax = gen.genPMax # set the max power to the nameplate capacity
            genFC.cubicSplineEstimator(powerStep) # calculate new fuel curve
            combFuelConsumption += [y for x, y in genFC.fuelCurve] # add the fuel consumption for each generator

        return zip(combFuelPower, list(combFuelConsumption)) # return list of tuples

    # genDispatch class method. Assigns a loading to each online generator and checks if they are inside operating bounds.
    # Inputs:
    # self - self reference
    # newGenP - new total generator real load
    # newGenQ - new total generator reactive load
    def genDispatch(self, newGenP, newGenQ):
        # dispatch
        if self.genDispatchType == 1: # if proportional loading
            # make sure to update genPAvail and genQAvail before
            loadingP = newGenP / self.genPAvail # this is the PU loading of each generator
            loadingQ = newGenQ / self.genQAvail  # this is the PU loading of each generator
            # cycle through each gen and update with new P and Q
            for idx in self.genIDS:
                self.generators.genP = loadingP * self.generators[idx].genPAvail
                self.generators.genQ = loadingQ * self.generators[idx].genQAvail
        else:
            print('The generator dispatch is not supported. ')

        # check operating bounds for each generator
        for idx in self.genIDS:
            self.generators[idx].checkOperatingCondtitions()
            # check if out of bounds
            self.outOfBounds[idx] = self.generators[idx].outOfBounds
            self.genSRC[idx] = self.generators[idx].genPAvail - self.generators[idx].genP


    # genSchedule class method. Brings another generator combination online
    # Inputs:
    # self - self reference
    # scheduledLoad - the load that the generators will be expected to supply, this is predicted based on previous loading
    # scheduledSRC -  the minimum spinning reserve that the generators will be expected to supply
    def genSchedule(self, scheduledLoad, scheduledSRC):
        ## first find all generator combinations that can supply the load within their operating bounds
        # find all with capacity over the load and the required SRC
        indCap = [idx for idx, x in enumerate(self.genCombinationsUpperNormalLoading) if x > scheduledLoad + scheduledSRC]
        # find all with MOL under the load
        indMOLCap = [idx for idx, x in enumerate(self.combinationsID[indCap]) if x < scheduledLoad]
        indInBounds = indCap[indMOLCap]

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
        for idx in indInBounds: # for each combination that is in bounds
            # inititiate the generators to be switched on for this combination to all generators in the combination
            genSwOn.append(self.genCombinationsID[idx])
            # initiate the generators to be switched off for this combination to all generators currently online
            genSwOff.append(self.genCombinationsID.index(self.genCombinationOnline))
            # find common elements between switch on and switch off lists
            commonGen = list(set(genSwOff).intersection(genSwOn))
            # remove common generators from both lists
            for genID in commonGen:
                genSwOn.remove(genID)
                genSwOff.remove(genID)
            # for each gen to be switched get time, max time for combination is time will take to bring online

            # find max time to switch generators online
            onTime = []
            for genID in genSwOn: # for each to be brought online
                onTime = max(onTime,turnOnTime[self.genIDS.index(genID)]) # max turn on time
            # find max of turn on time and turn off time
            SwitchTime = onTime # initiate to max turn on time
            for genID in genSwOff:
                SwitchTime = max(SwitchTime, turnOffTime[self.genIDS.index(genID)]) # check if there is a higher turn off time
            timeToSwitch.append(SwitchTime)

        ## then order the generator combinations based on their predicted fuel efficiency


        # bring the best option that can be switched immediatley, if any
        # if the most efficient option can't be switched, start warming up generators


