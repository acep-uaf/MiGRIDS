# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import Generator
import itertools

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
        for nGen in range(self.genIDS): # for all possible numbers of generators
            for subset in itertools.combinations(self.genIDS, nGen): # get all possible combinations with that number
                self.genCombinationsID.append(subset) # list of lists of gen IDs
                # get the minimum normal loading (if all operating at their MOL)
                subsetMOL = 0
                subsetGenUpperNormalLoading = 0 # the normal upper loading
                subsetGenUpperLimit = 0
                subsetGenLowerLimit = 0
                for gen in subset: # for each generator in the combination
                    subsetMOL += self.genMol[self.genIDS.index(gen)] # add the corresponding MOL for the generator
                    subsetGenUpperNormalLoading += self.genUpperNormalLoading[self.genIDS.index(gen)]
                    subsetGenUpperLimit += self.genUpperLimit[self.genIDS.index(gen)]
                    subsetGenLowerLimit += self.genLowerLimit[self.genIDS.index(gen)]
                self.genCombinationsMOL.append(subsetMOL)
                self.genCombinationsUpperNormalLoading.append(subsetGenUpperNormalLoading)
                self.genCombinationsUpperLimit.append(subsetGenUpperLimit)
                self.genCombinationsLowerLimit.append(subsetGenLowerLimit)

        # Update the current combination online
        for idx, combID in enumerate(self.combinationsID): # for each combination
            # get the gen IDs of online generators
            onlineGens = [genIDS[idx] for idx, x in enumerate(genStates) if x == 2]
            # if the gen IDs of this combination equal the gen IDs that are currently online, then this is current online combination
            if sorted(self.genCombinationsID[idx]) == sorted(onlineGens):
                self.genCombinationOnline = combID

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
            # TODO: add ability to adjust loading on other generators if able to avoid out of bounds operation on one
            self.outOfBounds[idx] = self.generators[idx].outOfBounds
            self.genSRC[idx] = self.generators[idx].genPAvail


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
            # need to get from genID to indicies
            # for each gen to be switched on or off
            for genID in genSwOff + genSwOn:
                timeToSwitch.append(max(timeToSwitch,turnOnTime[self.genIDS.index(genID)]))

        ## then order the generator combinations based on their predicted fuel efficiency
        # TODO: calculate combined fuel curve for gen combinations in init and use here to calculate efficiency of different options


        # bring the best option that can be switched immediatley, if any
        # if the most efficient option can't be switched, start warming up generators


