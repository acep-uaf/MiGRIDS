# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup
import os
#here = os.getcwd()
#os.chdir('../GBSAnalyzer/CurveAssemblers')
#from genFuelCurveAssembler import GenFuelCurve
#os.chdir(here)
import sys
sys.path.append('../')
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
        # TODO: what are these going to be used for? these should be used instead of PMax and QMax.
        self.genPAvail = self.genPMax  # De-rating or nameplate capacity [kW]
        self.genQAvail = self.genQMax  # De-rating or nameplate capacity [kvar]
        self.genMol = float(genSoup.mol.get('value')) * self.genPMax # the MOL, normal operation stay above this
        self.underMolLimit = float(genSoup.molLimit.get('value'))*self.genPMax # the maximum energy allowed below MOL in checkLoadingTime period
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
        self.genRunTimeMin = float(genSoup.minRunTime.get('value')) # minimum diesel run time
        self.genStartTime = float(genSoup.startTime.get('value')) # amount of time required to start from warm
        self.genStartCost =  float(genSoup.startCost.get('value')) # equivalent cost in kg of diesel to start engine

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
        genFC.cubicSplineCurveEstimator()
        self.genFuelCurve = genFC.fuelCurve  # TODO: consider making this the integer version.

    # Constructor
    def __init__(self, genID, genP, genQ, genState, timeStep, genDescriptor):
        """
        Constructor used for intialization of generator fleet in Powerhouse class.
        :param genID: integer for identification of object within Powerhouse list of generators.
        :param genP: initial real power level.
        :param genQ: initial reactive power level.
        :param genState: the current operating state, 0 - off, 1 - running, 2 - online.
        :param timeStep: the time step used in the simulation, in seconds.
        :param genDescriptor: relative path and file name of genDescriptor-file used to populate static information.
        """

        # Initiate current generator operation variables
        self.genRunTimeAct = 0  # Run time since last start [s]
        self.genRunTimeTot = 0  # Cummulative run time since model start [s]
        self.genStartTimeAct = 0  # the amount of time spent warming up
        self.prevLoading = [] # a list of the last x seconds of loading on the diesel generator, updated with checkOperatingConditions()

        # Write initial values to internal variables.
        self.genID = genID  # internal id used in Powerhouse for tracking generator objects. *type int*
        self.genP = genP  # Current real power level [kW]
        self.genQ = genQ  # Current reactive power level [kvar]
        self.genState = genState  # Generator operating state [dimensionless, index]. See docs for key.
        self.timeStep = timeStep  # the time step used in the simulation in seconds
        # initiate operating condition flags and timers
        self.outOfBounds = False  # indicates when the generator is operating above the upperLimit (see genDescriptor.xml) or below lowerLimit (see genDescriptor.xml)
        self.outOfNormalBounds = False  # indicates when the generator is operating above upperNormalLoadingLimit or below MOL
        self.overGenUpperNormalLoading = 0 # the amount by which the generator has operated above genUpperNormalLoading in the past self.checkLoadingTime
        self.genDescriptorParser(genDescriptor)

    def checkOperatingConditions(self):
        """
        Checks if the generator is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        # TODO: implement this, might include adding additional class-wide variables.

        ######### Check for out of bound operation ################
        # update the list of previous loadings and remove the oldest one
        self.prevLoading.append(self.genP)
        # limit the list to required length
        # first reverse order, then take checkLoadingTime of points and reverse back again
        # number of data points is (seconds required)/(# seconds per data point)
        self.prevLoading = self.prevLoading[::-1][:round(self.checkLoadingTime/self.timeStep)][::-1]

        ### Check the MOL constraint ###
        # subtract prevLoading from MOL to get under MOL generation
        molDifference = [self.genMol - x for x in self.prevLoading]
        # the amount of energy that has been operated below MOL in checkLoadingTime
        self.underMol = sum([num for num in molDifference if num > 0]) * self.timeStep

        ### Check the upper normal loading limit ###
        # subtract genUpperNormalLoading from prevLoading to get over genUpperNormalLoading generation
        normalUpperDifference = [x - self.genUpperNormalLoading for x in self.prevLoading]
        # the amount of energy that has been operated above genUpperNormalLoading in checkLoadingTime
        self.overGenUpperNormalLoading = sum([num for num in normalUpperDifference if num > 0]) * self.timeStep

        ### Check if out of bounds operation, then flag outOfNormalBounds ###
        # under MOL by specified amount and currently under
        if (self.underMol > self.underMolLimit) & (molDifference[-1] > 0):
            self.outOfNormalBounds = True
        # over normal max loading by specified amount and currently over
        elif (self.overGenUpperNormalLoading > self.genUpperNormalLoadingLimit) & (normalUpperDifference[-1] > 0):
            self.outOfNormalBounds = True
        # over the max loading
        elif self.genP > self.genUpperLimit:
            self.outOfNormalBounds = True
            self.outOfBounds = True # special flags for upper and lower bounds, for more immediate action by scheduler
        # under the min loading
        elif self.genP < self.genLowerLimit:
            self.outOfNormalBounds = True
            self.outOfBounds = True # special flags for upper and lower bounds, for more immediate action by scheduler
        # not out of bounds
        else:
            self.outOfNormalBounds = False


        ######## Update runtime timers and available power ##########
        # update run times
        if self.genState == 2: # if running online
            # the genStartTimeAct is not reset to zero here, because if the generator goes from running online to
            # running offline, it does not need to run for the full startTime. It is already warm and can be brought
            # directly back online
            self.genRunTimeAct += self.timeStep # increment run time since last started
            self.genRunTimeTot += self.timeStep # increment run time since beginning of sim
            # update available power
            self.genPAvail = self.genPMax
            self.genQAvail = self.genQMax

        elif self.genState == 1: # if running but offline (ie starting up)
            self.genRunTimeAct = 0  # if not running online, reset to zero
            self.genStartTimeAct += self.timeStep # the time it has been starting up for
            # update available power
            self.genPAvail = 0
            self.genQAvail = 0

        else: # if not running and offline
            self.genRunTimeAct = 0 # if not running online, reset to zero
            self.genStartTimeAct = 0 # if not starting reset to zero
            # update available power
            self.genPAvail = 0
            self.genQAvail = 0




