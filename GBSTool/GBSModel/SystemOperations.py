# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

from Powerhouse import Powerhouse
from Windfarm import Windfarm
#from SolarFarm import Solarfarm
from ElectricalEnergyStorageSystem import ElectricalEnergyStorageSystem
#from ThermalSystem import ThermalSystem
from Demand import Demand
import os
import sys
import importlib.util

class SystemOperations:
    # System Variables
    # Generation and dispatch resources
    def __init__(self, timeStep = 1, loadRealFiles = [], loadReactiveFiles = [], predictLoad = [],
                 genIDs = [], genStates = [], genDescriptors = [], genDispatch = [],
                 wtgIDs = [], wtgStates = [], wtgDescriptors = [], wtgSpeedFiles = [],
                 eesIDs = [], eesStates = [], eesSOCs = [], eesDescriptors = [], eesDispatch = []):
        """
        Constructor used for intialization of all sytem components
        :param timeStep: the length of time steps the simulation is run at in seconds.
        :param loadRealFiles: list of net cdf files that add up to the full real load
        :param loadReactiveFiles: list of net cdf files that add up to the full reactive load. This can be left empty.
        :param predictLoad: If a user defines their own load predicting function, it is the path and filename of the function used
        to predict short term (several hours) future load. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: predictLoad1. The class name in the file must be 'predictLoad'
        :param loadReactive: the net cdf file with the reactive load time series
        :param genIDS: list of generator IDs, which should be integers
        :param genP: list of generator real power levels for respective generators listed in genIDS
        :param genQ: list of generator reactive power levels for respective generators listed in genIDS
        :param genDescriptor: list of generator descriptor XML files for the respective generators listed in genIDS, this should
        be a string with a relative path and file name, e.g., /InputData/Components/gen1Descriptor.xml
        :param wtgIDS: list of wtg IDs, which should be integers
        :param wtgP: list of wtg real power levels for respective wtg listed in genIDS
        :param wtgQ: list of wtg reactive power levels for respective wtg listed in wtgIDS
        :param wtgStates: list of wind turbine operating states 0 - off, 1 - starting, 2 - online.
        :param wtgDescriptor: list of generator descriptor XML files for the respective generators listed in genIDS, this should
        be a string with a relative path and file name, e.g., /InputData/Components/wtg1Descriptor.xml
        :param eesIDS: list of integers for identification of Energy Storage units.
        :param eesSOC: list of initial state of charge.
        :param eesState: list of the initial operating state, 0 - off, 1 - starting, 2 - online.
        :param eesDescriptor: list of relative path and file name of eesDescriptor-files used to populate static information.
        :param eesDispatch: If a user defines their own dispatch, it is the path and filename of the dispatch class used
        to dispatch the energy storage units. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: eesDispatch1. The class name in the file must be 'eesDispatch'
        """
        # import the dispatch scheme
        # split into path and filename
        modPath, modFile = os.path.split(predictLoad)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        dispatchModule = importlib.import_module(modFileName)
        self.predictLoad = dispatchModule.predictLoad()

        # initiate generator power house
        # TODO: seperate genDispatch from power house, put as input
        if len(genIDs) != 0:
            self.PH = Powerhouse(genIDs, genStates, timeStep, genDescriptors)
        # initiate wind farm
        if len(wtgIDs) != 0:
            self.WF = Windfarm(wtgIDs, wtgSpeedFiles, wtgStates, timeStep, wtgDescriptors)
        # initiate electrical energy storage system
        if len(eesIDs) != 0:
            self.EESS = ElectricalEnergyStorageSystem(eesIDs, eesSOCs, eesStates, timeStep, eesDescriptors, eesDispatch)
        # load the real load
        if len(loadRealFiles) != 0:
            self.DM = Demand(timeStep, loadRealFiles, loadReactiveFiles)

    # TODO: Put in seperate input file
    def runSimulation(self):
        self.wtgPImport = []
        self.wtgPch = []
        self.srcMin = []
        self.eesDis = []
        self.genP = []
        self.genPAvail = []
        self.eessSrc = []
        self.eessSoc = []
        self.wtgPAvail = []
        self.rePlimit = []
        # record for trouble shooting purposes
        self.futureLoad = [0]*len(self.DM.realLoad)
        self.underSRC = [0]*len(self.DM.realLoad)
        self.outOfNormalBounds = [0]*len(self.DM.realLoad)
        self.genStartTime = []
        self.genRunTime = []

        for idx, P in enumerate(self.DM.realLoad[:1000]): #self.DM.realLoad: # for each real load
            ## Dispatch units
            # get available wind power
            wtgPAvail = sum(self.WF.wtgPAvail)
            # the maximum amount of power that can be imported from renewable resources
            rePlimit = max([P - sum(self.PH.genMolAvail),0])
            # amount of imported wind power
            wtgPimport = min(rePlimit,wtgPAvail)
            # amount of wind power used to charge the eess is the minimum of maximum charging power and the difference
            # between available wind power and wind power imported to the grid.
            wtgPch = min(sum(self.EESS.eesPinAvail),wtgPAvail - wtgPimport)
            # get the required spinning reserve. Start off with a simple estimate
            srcMin = 100 + wtgPimport
            # discharge the eess to cover the difference between load and generation
            eessDis = min([max([P - wtgPimport - sum(self.PH.genPAvail),0]),sum(self.EESS.eesPoutAvail)])
            # get the diesel power output, the difference between demand and supply
            genP = P - wtgPimport - eessDis
            # find the remaining ability of the EESS to supply SRC not supplied by the diesel generators
            eessSrcRequested = max([srcMin - sum(self.PH.genPAvail) + genP, 0])
            # dispatch the wind turbines
            self.WF.wtgDispatch(wtgPimport + wtgPch, 0)
            # dispatch the eess
            self.EESS.runEesDispatch(eessDis - wtgPch, 0, eessSrcRequested)
            # dispatch the generators
            self.PH.genDispatch(genP, 0)

            # record values
            self.rePlimit.append(rePlimit)
            self.wtgPAvail.append(wtgPAvail)
            self.wtgPImport.append(wtgPimport)
            self.wtgPch.append(wtgPch)
            self.srcMin.append(srcMin)
            self.eesDis.append(eessDis)
            self.genP.append(genP)
            self.genPAvail.append(sum(self.PH.genPAvail))
            self.eessSrc.append(self.EESS.eesSRC[:])
            self.eessSoc.append(self.EESS.eesSOC[:])
            # record for troubleshooting
            genStartTime = []
            genRunTime = []
            for gen in self.PH.generators:
                genStartTime.append(gen.genStartTime)
                genRunTime.append(gen.genRunTimeAct)
            self.genStartTime.append(genStartTime[:])
            self.genRunTime.append(genRunTime[:])

            ## If conditions met, schedule units
            # check if out of bounds opperation
            if any(self.EESS.underSRC) or any(self.EESS.outOfBoundsReal) or any(self.PH.outOfNormalBounds):
                # predict what load will be
                self.predictLoad.predictLoad(self.DM.realLoad[:idx+1], self.DM.realTime[idx])
                futureLoad = self.predictLoad.futureLoad
                # schedule the generators accordingly
                self.PH.genSchedule(futureLoad, 0)
                # TODO: incorporate energy storage capabilities and wind power into diesel schedule. First predict
                # the future amount of wind power. find available SRC from EESS. Accept the amount of predicted wind
                # power that can be covered by ESS (likely some scaling needed to avoid switching too much)
                # record for trouble shooting purposes
                self.futureLoad[idx] = futureLoad
                if any(self.EESS.underSRC):
                    self.underSRC[idx] = 1
                if any(self.PH.outOfNormalBounds):
                    self.outOfNormalBounds[idx] = 1


