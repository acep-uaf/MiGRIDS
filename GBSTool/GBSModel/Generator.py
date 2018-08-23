# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
import sys
import os
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
from bs4 import BeautifulSoup as Soup
from GBSAnalyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve


class Generator:
    '''
    Generator class: contains all necessary information for a single generator. Multiple generators are aggregated in a
    Powerhouse object (see Powerhouse.py), which further is aggregated in the SystemOperations object (see
    SystemOperations.py).
    '''

    # Generator descriptor parser
    def genDescriptorParser(self, genDescriptor):
        """
        Reads the data from a given genDescriptor file and uses the information given to populate the
        respective internal variables.

        :param genDescriptor: relative path and file name of genDescriptor.xml-file that is used to populate static
        information

        :return:
        """

        # read xml file
        genDescriptorFile = open(genDescriptor, "r")
        genDescriptorXml = genDescriptorFile.read()
        genDescriptorFile.close()
        genSoup = Soup(genDescriptorXml, "xml")

        # Dig through the tree for the required data
        self.genName = genSoup.component.get('name')
        self.genPMax = float(genSoup.POutMaxPa.get('value')) # nameplate capacity
        self.genQMax = float(genSoup.QOutMaxPa.get('value'))  # nameplate capacity kvar
        self.genMol = float(genSoup.mol.get('value')) * self.genPMax # the MOL, normal operation stay above this
        self.underMolLimit = float(genSoup.molLimit.get('value'))*self.genPMax # the maximum energy allowed below MOL in checkLoadingTime period
        self.genMel = float(genSoup.mel.get('value')) * self.genPMax  # the MEL, efficient operation is above this
        self.underMelLimit = float(genSoup.melLimit.get(
            'value')) * self.genPMax  # the maximum energy allowed below MEL in checkLoadingTime period
        # the loading above which normal operation stays below.
        self.genUpperNormalLoading = float(genSoup.upperNormalLoading.get('value'))*self.genPMax
        # the maximum amount of energy allowed above the normal upper limit in a checkLoadingTime period
        self.genUpperNormalLoadingLimit = float(genSoup.upperNormalLoadingLimit.get('value'))*self.genPMax
        # the lowest loading below which will immediatly flag the scheduler
        self.genLowerLimit = float(genSoup.lowerLimit.get('value'))*self.genPMax
        # The highest loading above which will immediatly flag the scheduler
        self.genUpperLimit = float(genSoup.upperLimit.get('value'))*self.genPMax
        # the amount of time in seconds that the loading on the diesel generators is monitored for
        self.checkLoadingTime = float(genSoup.checkLoadingTime.get('value'))
        # Helper variable to find the first index (from the back) in the lists keeping track of previous loading,
        # molDifference and normalUpperDifference in checkOperatingConditions
        self.checkLoadTimeIdx = -round(self.checkLoadingTime / self.timeStep) + 1
        self.genRunTimeMin = float(genSoup.minRunTime.get('value')) # minimum diesel run time
        self.genStartTime = float(genSoup.startTime.get('value')) # amount of time required to start from warm
        self.genStartCost =  float(genSoup.startCost.get('value')) # equivalent cost in kg of diesel to start engine
        # get diesel charging of ESS constraints
        self.maxDiesCapCharge = list(zip([float(x) for x in genSoup.maxDiesCapCharge.e.get('value').split()],
                                    [float(x) for x in genSoup.maxDiesCapCharge.mdcc.get('value').split()]))

        # Handle the fuel curve interpolation
        fuelCurvePPuInpt = genSoup.fuelCurve.pPu.get('value').split()
        fuelCurveMFInpt = genSoup.fuelCurve.massFlow.get('value').split()
        if len(fuelCurvePPuInpt) != len(fuelCurveMFInpt):  # check that both input lists are of the same length
            raise ValueError('Fuel curve calculation error: Power and mass flow lists are not of same length.')

        fuelCurveData = []
        for idx, item in enumerate(fuelCurvePPuInpt):
            fuelCurveData.append((self.genPMax * float(fuelCurvePPuInpt[idx]), float(fuelCurveMFInpt[idx])))
        genFC = GenFuelCurve()
        genFC.fuelCurveDataPoints = fuelCurveData
        genFC.genOverloadPMax = self.genPMax  # TODO: consider making this something else.
        genFC.linearCurveEstimator()
        self.genFuelCurve = genFC.fuelCurve  # TODO: consider making this the integer version.

    # Constructor
    def __init__(self, genID, genState, timeStep, genDescriptor):
        """
        Constructor used for intialization of generator fleet in Powerhouse class.
        :param genID: integer for identification of object within Powerhouse list of generators.
        :param genState: the current operating state, 0 - off, 1 - running, 2 - online.
        :param timeStep: the time step used in the simulation, in seconds.
        :param genDescriptor: relative path and file name of genDescriptor-file used to populate static information.
        """

        # Initiate current generator operation variables
        self.genRunTimeAct = 0  # Run time since last start [s]
        self.genRunTimeTot = 0  # Cummulative run time since model start [s]
        self.genStartTimeAct = 0  # the amount of time spent warming up
        self.prevLoading = [0] # a list of the last x seconds of loading on the diesel generator, updated with checkOperatingConditions()
        self.molDifference = [0] # a list of the last x seconds with the amount operated below MOL
        self.melDifference = [0]  # a list of the last x seconds with the amount operated below MEL
        self.normalUpperDifference = [0] # a list of the last x seconds with the amount operated above normalUpperLimit

        # Write initial values to internal variables.
        self.genID = genID  # internal id used in Powerhouse for tracking generator objects. *type int*
        self.genP = 0  # Current real power level [kW]
        self.genQ = 0  # Current reactive power level [kvar]
        self.genState = genState  # Generator operating state [dimensionless, index]. See docs for key.
        self.timeStep = timeStep  # the time step used in the simulation in seconds
        # initiate operating condition flags and timers
        self.outOfBounds = False  # indicates when the generator is operating above the upperLimit (see genDescriptor.xml) or below lowerLimit (see genDescriptor.xml)
        self.outOfNormalBounds = False  # indicates when the generator is operating above upperNormalLoadingLimit or below MOL
        self.outOfEfficientBounds = False
        self.overGenUpperNormalLoading = 0 # the amount by which the generator has operated above genUpperNormalLoading in the past self.checkLoadingTime
        self.underMol = 0 # the amount by which operating below MOL
        self.underMel = 0  # the amount by which operating below MEL (minimum efficient operation, set >= MOL)
        self.genDescriptorParser(genDescriptor)
        # update genMolAvail, genPAvail and genQAvail depending on Gstate
        if genState == 2:
            self.genPAvail = self.genPMax # P available is the how much power is avialable online. P max if online, 0 otherwise
            self.genQAvail = self.genQMax
            self.genMolAvail = self.genMol # the lowest loading it can run at
            self.genMelAvail = self.genMel
        else:
            self.genPAvail = 0
            self.genQAvail = 0
            self.genMolAvail = 0
            self.genMelAvail = 0

    def checkOperatingConditions(self):
        """
        Checks if the generator is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        # TODO: implement this, might include adding additional class-wide variables.

        # only need to check if online, otherwise not out of bounds
        if self.genState == 2:
            ######### Check for out of bound operation ################
            # update the list of previous loadings and remove the oldest one
            # limit the list to required length
            self.prevLoading = self.prevLoading[self.checkLoadTimeIdx:] + [self.genP]

            ### Check the MOL constraint ###
            '''
            # subtract prevLoading from MOL to get under MOL generation
            molDifference = [self.genMol - x for x in self.prevLoading]
            # the amount of energy that has been operated below MOL in checkLoadingTime
            self.underMol = sum([num for num in molDifference if num > 0]) * self.timeStep
            '''
            # try faster check - see issue #113 and #114 for explanation
            molDifference0 = self.molDifference[0]
            self.molDifference = self.molDifference[self.checkLoadTimeIdx:] + [max([self.genMol - self.genP,0])]
            self.underMol = self.underMol - (molDifference0 - self.molDifference[-1])*self.timeStep

            ### Check the MEL (minimum economic loading) constraint ###
            melDifference0 = self.melDifference[0]
            self.melDifference = self.melDifference[self.checkLoadTimeIdx:] + [max([self.genMel - self.genP, 0])]
            self.underMel = self.underMel - (melDifference0 - self.melDifference[-1]) * self.timeStep

            ### Check the upper normal loading limit ###
            '''
            # subtract genUpperNormalLoading from prevLoading to get over genUpperNormalLoading generation
            normalUpperDifference = [x - self.genUpperNormalLoading for x in self.prevLoading]
            # the amount of energy that has been operated above genUpperNormalLoading in checkLoadingTime
            self.overGenUpperNormalLoading = sum([num for num in normalUpperDifference if num > 0]) * self.timeStep
            '''

            # try faster check -  see issue #113 and #114 for explanation
            normalUpperDifference0 = self.normalUpperDifference[0]
            self.normalUpperDifference = self.normalUpperDifference[self.checkLoadTimeIdx:] + [
                max([self.genP - self.genUpperNormalLoading, 0])]
            # try faster check
            self.overGenUpperNormalLoading = self.overGenUpperNormalLoading - \
                                             (normalUpperDifference0 - self.normalUpperDifference[-1]) * self.timeStep

            ### Check if out of bounds operation, then flag outOfNormalBounds ###
            # under MEL by specified amount and currently under
            if (self.underMel > self.underMelLimit) & (self.melDifference[-1] > 0):
                self.outOfEfficientBounds = True

                # check if also under MOL
                if (self.underMol > self.underMolLimit) & (self.molDifference[-1] > 0):
                    self.outOfNormalBounds = True

                    # check if also under lower limit
                    # under the min loading
                    if self.genP < self.genLowerLimit:
                        self.outOfBounds = True  # special flags for upper and lower bounds, for more immediate action by scheduler
                    else:
                        self.outOfBounds = False

                else:
                    self.outOfNormalBounds = False
                    self.outOfBounds = False
            # if not under MEL, check if over normal upper loading
            elif (self.overGenUpperNormalLoading > self.genUpperNormalLoadingLimit) & (
                        self.normalUpperDifference[-1] > 0):
                self.outOfNormalBounds = True
                self.outOfEfficientBounds = False
                # check if also over upper limit
                if self.genP > self.genUpperLimit:
                    self.outOfBounds = True  # special flags for upper and lower bounds, for more immediate action by scheduler

            # not out of any bounds
            else:
                self.outOfEfficientBounds = False
                self.outOfBounds = False
                self.outOfNormalBounds = False

            ######## Update runtime timers and available power ##########
            # update run times
            # the genStartTimeAct is not reset to zero here, because if the generator goes from running online to
            # running offline, it does not need to run for the full startTime. It is already warm and can be brought
            # directly back online
            self.genRunTimeAct += self.timeStep # increment run time since last started
            self.genRunTimeTot += self.timeStep # increment run time since beginning of sim
            # update available power
            self.genPAvail = self.genPMax
            self.genQAvail = self.genQMax
            self.genMolAvail = self.genMol  # the lowest loading it can run at
            self.genMelAvail = self.genMel

        elif self.genState == 1: # if running but offline (ie starting up)
            # update timers
            self.genRunTimeAct = 0  # if not running online, reset to zero
            self.genStartTimeAct += self.timeStep # the time it has been starting up for
            # update available power
            self.genPAvail = 0
            self.genQAvail = 0
            self.genMolAvail = 0  # the lowest loading it can run at
            self.genMelAvail = 0

            ### Check if out of bounds operation, then flag outOfNormalBounds ###
            if self.genP > 0:
                self.outOfNormalBounds = True
                self.outOfBounds = True
            else:
                self.outOfNormalBounds = False
                self.outOfBounds = False

        else: # if not running and offline
            # update timers
            self.genRunTimeAct = 0 # if not running online, reset to zero
            self.genStartTimeAct = 0 # if not starting reset to zero
            # update available power
            self.genPAvail = 0
            self.genQAvail = 0
            self.genMolAvail = 0  # the lowest loading it can run at
            self.genMelAvail = 0

            ### Check if out of bounds operation, then flag outOfNormalBounds ###
            if self.genP > 0:
                self.outOfNormalBounds = True
                self.outOfBounds = True
            else:
                self.outOfNormalBounds = False
                self.outOfBounds = False


