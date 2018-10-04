# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import itertools
import sys
import os
import numpy as np
import importlib.util
from GBSModel.Generator import Generator
from bs4 import BeautifulSoup as Soup
sys.path.append('../')
from GBSAnalyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve
from GBSModel.getIntListIndex import getIntListIndex
import xml.etree.ElementTree as ET
from GBSModel.loadControlModule import loadControlModule


class Powerhouse:
    # __init()__ Class constructor. Initiates the setup of the individual generators as per the initial input.
    # Inputs:
    # self - self reference, always required in constructor
    # genIDS - list of generator IDs, which should be integers
    # genP - list of generator real power levels for respective generators listed in genIDS
    # genQ - list of generator reactive power levels for respective generators listed in genIDS
    # genDescriptor - list of generator descriptor XML files for the respective generators listed in genIDS, this should
    #   be a string with a relative path and file name, e.g., /InputData/Components/gen1Descriptor.xml
    def __init__(self, genIDS, genStates, timeStep, genDescriptor, genDispatchFile, genScheduleFile,
                 genDispatchInputsFile, genScheduleInputsFile):
        # check to make sure same length data coming in
        if not len(genIDS)==len(genStates):
            raise ValueError('The length genIDS, genP, genQ and genStates inputs to Powerhouse must be equal.')
        # ************Powerhouse variables**********************
        # general
        self.timeStep = timeStep
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
        self.outOfEfficientBounds = []
        self.genMol = []
        self.genMel = []
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
        # the minimum efficient power output based on MEL
        self.genMelAvail = []



        ## initiate generator dispatch and its inputs.
        # import gen energy dispatch
        self.genDispatch = loadControlModule(genDispatchFile, genDispatchInputsFile, 'genDispatch')
        self.genSchedule = loadControlModule(genScheduleFile, genScheduleInputsFile, 'genSchedule')
        """
        modPath, modFile = os.path.split(genDispatchFile)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        A = importlib.import_module(modFileName)
        # get the inputs
        rdi = open(genDispatchInputsFile, "r")
        genDispatchInputsXml = rdi.read()
        rdi.close()
        genDispatchInputsSoup = Soup(genDispatchInputsXml, "xml")

        # get all tags
        elemList = []
        xmlTree = ET.parse(genDispatchInputsFile)
        for elem in xmlTree.iter():
            elemList.append(elem.tag)

        # create Dict of tag names and values (not including root)
        genDispatchInputs = {}
        for elem in elemList[1:]:
            genDispatchInputs[elem] = self.returnObjectValue(genDispatchInputsSoup.find(elem).get('value'))

        # check if inputs for initializing genDispatch
        if len(genDispatchInputs) == 0:
            self.genDispatch = A.genDispatch()
        else:
            self.genDispatch = A.genDispatch(genDispatchInputs)
        
        ## initiate generator schedule and its inputs.
        # import gen energy dispatch
        modPath, modFile = os.path.split(genScheduleFile)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        A = importlib.import_module(modFileName)
        # get the inputs
        rdi = open(genScheduleInputsFile, "r")
        genScheduleInputsXml = rdi.read()
        rdi.close()
        genScheduleInputsSoup = Soup(genScheduleInputsXml, "xml")

        # get all tags
        elemList = []
        xmlTree = ET.parse(genScheduleInputsFile)
        for elem in xmlTree.iter():
            elemList.append(elem.tag)

        # create Dict of tag names and values (not including root)
        genScheduleInputs = {}
        for elem in elemList[1:]:
            genScheduleInputs[elem] = self.returnObjectValue(genScheduleInputsSoup.find(elem).get('value'))

        # check if inputs for initializing genDispatch
        if len(genScheduleInputs) == 0:
            self.genSchedule = A.genSchedule()
        else:
            self.genSchedule = A.genSchedule(genScheduleInputs)
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
            self.genMelAvail += [self.generators[idx].genMelAvail]
            self.outOfNormalBounds.append(self.generators[idx].outOfNormalBounds)
            self.outOfBounds.append(self.generators[idx].outOfBounds)
            self.outOfEfficientBounds.append(self.generators[idx].outOfEfficientBounds)
            self.genMol.append(self.generators[idx].genMol) # the MOLs of each generator
            self.genMel.append(self.generators[idx].genMel)
            self.genUpperNormalLoading.append(self.generators[idx].genUpperNormalLoading)  # the genUpperNormalLoading of each generator
            self.genUpperLimit.append(self.generators[idx].genUpperLimit) # the upper limit of each generator
            self.genLowerLimit.append(self.generators[idx].genLowerLimit) # the lower limit of each generator
        # Create a list of all possible generator combination ID, MOL, upper normal loading, upper limit and lower limit
        # these will be used to schedule the diesel generators
        self.combinationsID = range(2**len(self.genIDS)) # the IDs of the generator combinations
        self.genCombinationsID = [] # the gen IDs in each combination
        self.genCombinationsMOL = np.array([])
        self.genCombinationsMEL = np.array([])
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
                subsetMELPU = 0
                subsetGenUpperNormalLoading = 0 # the normal upper loading
                subsetGenUpperLimit = 0
                subsetGenLowerLimit = 0
                subsetPMax = 0
                powerLevelsPU = [] # pu power levels in combined fuel curve for combination
                fuelConsumption = [] # fuel consumption for combined fuel curve
                for gen in subset: # for each generator in the combination
                    subsetPMax += self.generators[self.genIDS.index(gen)].genPMax
                    subsetMOLPU = max(subsetMOLPU,self.genMol[self.genIDS.index(gen)]/self.generators[self.genIDS.index(gen)].genPMax) # get the max pu MOL of the generators
                    subsetMELPU = max(subsetMELPU, self.genMel[self.genIDS.index(gen)] / self.generators[
                        self.genIDS.index(gen)].genPMax)
                    subsetGenUpperNormalLoading += self.genUpperNormalLoading[self.genIDS.index(gen)]
                    subsetGenUpperLimit += self.genUpperLimit[self.genIDS.index(gen)]
                    subsetGenLowerLimit += self.genLowerLimit[self.genIDS.index(gen)]

                self.genCombinationsMOL = np.append(self.genCombinationsMOL, subsetMOLPU*subsetPMax) # pu MOL * P max =  MOL
                self.genCombinationsMEL = np.append(self.genCombinationsMEL, subsetMELPU * subsetPMax)
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

        # CREATE LOOKUP TABLES FOR GENDISPATCH
        # UPPER NORMAL LOADING
        # Setup a list of all possible 'loading' values
        # Max combination will be needed during lookups as default value to revert to if there is no list of available
        # combinations for a lookup key, i.e., if the load is greater than the max upper normal loading of any gen comb.
        self.genCombinationsUpperNormalLoadingMaxIdx = int(np.argmax(np.asarray(self.genCombinationsUpperNormalLoading)))
        loading = list(range(0, int(max(self.genCombinationsUpperNormalLoading)+1)))
        self.lkpGenCombinationsUpperNormalLoading = {}
        for load in loading:
            combList = np.array([], dtype=int)
            for idy, genComb in enumerate(self.genCombinationsUpperNormalLoading):
                if load <= genComb:
                    combList = np.append(combList, idy)
            self.lkpGenCombinationsUpperNormalLoading[load] = combList

        # CALCULATE AND SAVE THE MAXIMUM GENERATOR START TIME
        # this is used in the generator scheduling.
        self.maxStartTime = 0
        for gen in self.generators:
            self.maxStartTime = max(self.maxStartTime, gen.genStartTime)




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
    def runGenDispatch(self, newGenP, newGenQ):
        self.genDispatch.runDispatch(self, newGenP, newGenQ)
        """     
        # dispatch
        if self.genDispatchType == 1: # if proportional loading
            # make sure to update genPAvail and genQAvail before
            # check if no diesel generators online. still assign power, this will be flagged as a power outage
            # Helper sum
            sumGenPAvail = sum(self.genPAvail)
            if sumGenPAvail == 0:
                for idx in range(len(self.genIDS)):
                    self.generators[idx].genP = newGenP/len(self.genIDS)
                    self.generators[idx].genQ = newGenQ/len(self.genIDS)
                    # update the local variable that keeps track of generator power
                    self.genP[idx] = self.generators[idx].genP
                    self.genQ[idx] = self.generators[idx].genQ
            else:
                loadingP = newGenP / max(sumGenPAvail, 1) # this is the PU loading of each generator. max with 1 for 0 capacity instance
                loadingQ = newGenQ / max(sum(self.genQAvail),1)  # this is the PU loading of each generator
                # cycle through each gen and update with new P and Q
                for idx in range(len(self.genIDS)):
                    self.generators[idx].genP = loadingP * self.generators[idx].genPAvail
                    self.generators[idx].genQ = loadingQ * self.generators[idx].genQAvail
                    # update the local variable that keeps track of generator power
                    self.genP[idx] = self.generators[idx].genP
                    self.genQ[idx] = self.generators[idx].genQ
        else:
            print('The generator dispatch is not supported. ')
        """
        # check operating bounds for each generator
        for idx in range(len(self.genIDS)):
            self.generators[idx].checkOperatingConditions()
            # check if out of bounds
            self.outOfNormalBounds[idx] = self.generators[idx].outOfNormalBounds
            self.outOfBounds[idx] = self.generators[idx].outOfBounds
            self.outOfEfficientBounds[idx] = self.generators[idx].outOfEfficientBounds
            # get available power and minimum loading from each
            self.genPAvail[idx] = self.generators[idx].genPAvail
            self.genQAvail[idx] = self.generators[idx].genQAvail
            self.genMolAvail[idx] = self.generators[idx].genMolAvail
            self.genMelAvail[idx] = self.generators[idx].genMelAvail
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
    def runGenSchedule(self, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay, powerAvailToSwitch, powerAvailToStay,underSRC):
        self.genSchedule.runSchedule(self, futureLoad, futureRE, scheduledSRCSwitch, scheduledSRCStay,
                                     powerAvailToSwitch, powerAvailToStay,underSRC)

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



