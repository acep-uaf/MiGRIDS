# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import importlib.util
import os
import sys

import numpy as np

# from ThermalSystem import ThermalSystem
from GBSModel.Demand import Demand
# from SolarFarm import Solarfarm
from GBSModel.ElectricalEnergyStorageSystem import ElectricalEnergyStorageSystem
from GBSModel.Powerhouse import Powerhouse
from GBSModel.Windfarm import Windfarm


class SystemOperations:
    # System Variables
    # Generation and dispatch resources
    def __init__(self, timeStep = 1, runTimeSteps = 'all', loadRealFiles = [], loadReactiveFiles = [], predictLoad = 'predictLoad1',
                 predictWind = 'predictWind0', getMinSrcFile = 'getMinSrc0',
                 genIDs = [], genStates = [], genDescriptors = [], genDispatch = [],
                 wtgIDs = [], wtgStates = [], wtgDescriptors = [], wtgSpeedFiles = [], wtgDispatch = [],
                 eesIDs = [], eesStates = [], eesSOCs = [], eesDescriptors = [], eesDispatch = []):
        """
        Constructor used for intialization of all sytem components
        :param timeStep: the length of time steps the simulation is run at in seconds.
        :param runTimeSteps: the timesteps to run. This can be 'all', an interger that the simulation runs up till, a list
        of two values of the start and stop indecies, or a list of indecies of length greater than 2 to use directly.
        :param loadRealFiles: list of net cdf files that add up to the full real load
        :param loadReactiveFiles: list of net cdf files that add up to the full reactive load. This can be left empty.
        :param predictLoad: If a user defines their own load predicting function, it is the path and filename of the function used
        to predict short term (several hours) future load. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: predictLoad0. The class name in the file must be 'predictLoad'. Inputs to the class are
        the load profile up till the current time step and the date-time in epoch format.
        :param predictWind: If a user defines their own wind predicting function, it is the path and filename of the function used
        to predict short term (several hours) future wind power. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: predictWind0. The class name in the file must be 'predictWind'. Inputs to the class are
        the wind profile up till the current time step and the date-time in epoch format.
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
        package. Options include: eesDispatch0. The class name in the file must be 'eesDispatch'
        """

        # import the load predictor
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

        # import the wind predictor
        # split into path and filename
        modPath, modFile = os.path.split(predictWind)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        dispatchModule = importlib.import_module(modFileName)
        self.predictWind = dispatchModule.predictWind()

        # import min src calculator
        modPath, modFile = os.path.split(getMinSrcFile)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        A = importlib.import_module(modFileName)
        self.getMinSrc = A.getMinSrc
        #self.getMinSrc = getMinSrc.getMinSrc()

        # initiate generator power house
        # TODO: seperate genDispatch from power house, put as input
        if len(genIDs) != 0:
            self.PH = Powerhouse(genIDs, genStates, timeStep, genDescriptors)
        # initiate wind farm
        if len(wtgIDs) != 0:
            self.WF = Windfarm(wtgIDs, wtgSpeedFiles, wtgStates, timeStep, wtgDescriptors, runTimeSteps)
        # initiate electrical energy storage system
        if len(eesIDs) != 0:
            self.EESS = ElectricalEnergyStorageSystem(eesIDs, eesSOCs, eesStates, timeStep, eesDescriptors, eesDispatch)
        # load the real load
        if len(loadRealFiles) != 0:
            self.DM = Demand(timeStep, loadRealFiles, loadReactiveFiles, runTimeSteps)

        # save local variables
        self.timeStep = timeStep

    # TODO: Put in seperate input file
    def runSimulation(self):
        self.wtgPImport = []
        self.wfPImport = []
        self.wtgP = []
        self.wfPch = []
        self.wfPTot = []
        self.srcMin = []
        self.eessDis = []
        self.eessP = []
        self.eesPLoss = []
        self.powerhouseP = []
        self.genP = []
        self.genPAvail = []
        self.eessSrc = []
        self.eessSoc = []
        self.wfPAvail = []
        self.wtgPAvail = []
        self.rePlimit = []
        # record for trouble shooting purposes
        self.futureLoad = [0]*len(self.DM.realLoad)
        self.futureWind = [[0]*len(self.WF.windTurbines)] * len(self.DM.realLoad)
        self.futureSRC = [0] * len(self.DM.realLoad)
        self.underSRC = [0]*len(self.DM.realLoad)
        self.outOfNormalBounds = [0]*len(self.DM.realLoad)
        self.genStartTime = []
        self.genRunTime = []
        self.onlineCombinationID = []

        # FUTUREFEATURE: run through parts of the year at a time and save the output.
        for idx, P in enumerate(self.DM.realLoad): #self.DM.realLoad: # for each real load
            ## Dispatch units
            # get available wind power
            wfPAvail = sum(self.WF.wtgPAvail)
            # the maximum amount of power that can be imported from renewable resources
            rePlimit = max([P - sum(self.PH.genMolAvail),0])
            # amount of imported wind power
            wtgPimport = min(rePlimit,wfPAvail)
            # amount of wind power used to charge the eess is the minimum of maximum charging power and the difference
            # between available wind power and wind power imported to the grid.
            # TODO: put condition if to charge ESS here
            wtgPch = min(sum(self.EESS.eesPinAvail),wfPAvail - wtgPimport)

            # TODO: put TES charging here

            # dispatch the wind turbines
            self.WF.wtgDispatch(wtgPimport + wtgPch, 0)
            # get the required spinning reserve. Start off with a simple estimate
            srcMin = self.getMinSrc(self.WF.wtgP, self.WF.wtgMinSrcCover, self.DM.realLoad[:idx+1], self.timeStep)

            #srcMin = 100 + wtgPimport
            # discharge the eess to cover the difference between load and generation
            eessDis = min([max([P - wtgPimport - sum(self.PH.genPAvail),0]),sum(self.EESS.eesPoutAvail)])
            # get the diesel power output, the difference between demand and supply
            phP = P - wtgPimport - eessDis
            # find the remaining ability of the EESS to supply SRC not supplied by the diesel generators
            eessSrcRequested = max([srcMin[0] - sum(self.PH.genPAvail) + phP, 0])

            # TODO: test the diesel charging of ESS here
            # for each energy storage unit SOC, find the appropriate diesel charging power based on the scheduled power
            # get the charging rules for the generators
            # find the loading on the generators
            phLoadMax = []
            for idx, eesSOC in enumerate(self.EESS.eesSOC):
                #find the SOC
                genMaxLoad, eesMaxSOC = zip(*self.PH.genMaxDiesCapCharge)
                # find the lowest max SOC the SOC of the ees is under
                idxSOC = idxSOC + [np.where(eesMaxSOC > eesSOC)[0]]
                if len(idxSOC) == 0 :
                    idxSOC = len(eesMaxSOC)-1
                # use the max loading of all the EES that the gens are allowed to go to
                phLoadMax = max(phLoadMax,genMaxLoad[idxSOC])

            # find the increase in loading
            phPch = max(phLoadMax - phP / sum(self.PH.genPAvail), 0) * sum(self.PH.genPAvail)
            # only able to charge as much as is left over from being charged from wind power
            phPch = min(sum(self.EESS.eesPinAvail) - wtgPch, phPch )

            # dispatch the eess
            self.EESS.runEesDispatch(eessDis - wtgPch - phPch, 0, eessSrcRequested)
            # read what eess managed to do
            eessP = sum(self.EESS.eesP[:])
            # recalculate firm generator power required
            phP = P - wtgPimport - max([eessP,0]) + phPch

            # dispatch the generators
            self.PH.genDispatch(phP, 0)

            # record values
            self.rePlimit.append(rePlimit)
            self.wfPAvail.append(wfPAvail) # wind farm p avail
            self.wtgPAvail.append(self.WF.wtgPAvail[:]) # list of wind turbines  p avail
            self.wfPImport.append(wtgPimport) #
            self.wtgP.append(self.WF.wtgP)
            self.wfPch.append(wtgPch)
            self.wfPTot.append(wtgPch+wtgPimport)
            self.srcMin.append(srcMin[0])
            self.eessDis.append(eessDis)
            self.eessP.append(eessP)
            self.eesPLoss.append(self.EESS.eesPloss[:])
            self.powerhouseP.append(phP)
            self.genP.append(self.PH.genP[:])
            self.genPAvail.append(sum(self.PH.genPAvail))
            self.eessSrc.append(self.EESS.eesSRC[:])
            self.eessSoc.append(self.EESS.eesSOC[:])
            self.onlineCombinationID.append(self.PH.onlineCombinationID)
            # record for troubleshooting
            genStartTime = []
            genRunTime = []
            for gen in self.PH.generators:
                genStartTime.append(gen.genStartTimeAct)
                genRunTime.append(gen.genRunTimeAct)
            self.genStartTime.append(genStartTime[:])
            self.genRunTime.append(genRunTime[:])

            ## If conditions met, schedule units
            # check if out of bounds opperation
            if any(self.EESS.underSRC) or any(self.EESS.outOfBoundsReal) or any(self.PH.outOfNormalBounds) or \
                    any(self.WF.wtgSpilledWindFlag):
                # predict what load will be
                # the previous 24 hours. 24hr * 60min/hr * 60sec/min = 86400 sec.
                self.predictLoad.predictLoad(self.DM.realLoad[:idx+1], self.DM.realTime[idx])
                futureLoad = self.predictLoad.futureLoad

                # predict what the wind will be
                self.predictWind.predictWind(self.WF.wtgPAvail, self.DM.realTime[idx])
                futureWind = self.predictWind.futureWind

                # TODO: add other RE

                # get the ability of the energy storage system to supply SRC
                eesSrcAvailMax = [] # the amount of SRC available from all ees units
                # iterate through all ees and add their available SRC
                for ees in self.EESS.electricalEnergyStorageUnits:
                    eesSrcAvailMax.append(ees.findPdisAvail(ees.eesSrcTime, 0, 0))

                # find the required capacity of the diesel generators
                # how much SRC can EESS cover? This can be subtracted from the load that the diesel generators must be
                # able to supply
                if sum(futureWind) > futureLoad: # if wind is greater than load, scale back to equal the load
                    ratio = futureLoad/sum(futureWind)
                    futureWind = [x*ratio for x in futureWind]
                futureSRC = self.getMinSrc(futureWind, self.WF.wtgMinSrcCover, futureLoad, self.timeStep)
                # check if available SRC from EES is zero, to avoid dividing by zero
                if sum(eesSrcAvailMax) > 0:
                    coveredSRCStay = min([sum(eesSrcAvailMax), futureSRC[0]])
                    coveredSRCSwitch = min([sum(eesSrcAvailMax), futureSRC[1]])
                    # get the amount of SRC provided by each ees
                    eesSrcScheduledStay = np.array(eesSrcAvailMax)*coveredSRCStay/sum(eesSrcAvailMax)
                    eesSrcScheduledSwitch = np.array(eesSrcAvailMax) * coveredSRCSwitch / sum(eesSrcAvailMax)
                else:
                    coveredSRCStay = 0
                    coveredSRCSwitch = 0
                    eesSrcScheduledStay = 0
                    eesSrcScheduledSwitch = 0

                # get the ability of the energy storage system to supply the load by discharging, on top of the RE it is
                # covering with SRC
                eesSchedDischAvail = 0  # the amount of discharge available from all ees units for specified amount of time
                # iterate through all ees and add their available discharge
                for index, ees in enumerate(self.EESS.electricalEnergyStorageUnits):
                    # if generators running online, only schedule the ESS to be able to discharge if over the min SOC
                    # the problem is that this will not
                    if ees.eesSOC > ees.eesDispatchMinSoc:
                        # find the loss associated with the spinning reserve
                        eesLoss = ees.findLoss(eesSrcScheduledSwitch[index], ees.eesSrcTime)
                        # calculate the available discharge, taking into account the amount reserved to supply SRC and the
                        # energy capacity required taking into account losses
                        eesSchedDischAvail += ees.findPdisAvail(ees.eesDispatchTime, eesSrcScheduledSwitch[index], eesLoss + ees.eesSrcTime*eesSrcScheduledSwitch[index])

                # schedule the generators accordingly
                self.PH.genSchedule(futureLoad, sum(futureWind), futureSRC[1] - coveredSRCSwitch, futureSRC[0] - coveredSRCStay,
                                    eesSchedDischAvail, sum(eesSrcAvailMax) - sum(eesSrcScheduledStay))
                # TODO: incorporate energy storage capabilities and wind power into diesel schedule. First predict
                # the future amount of wind power. find available SRC from EESS. Accept the amount of predicted wind
                # power that can be covered by ESS (likely some scaling needed to avoid switching too much)

                # record for trouble shooting purposes
                self.futureLoad[idx] = futureLoad
                self.futureWind[idx] = futureWind
                self.futureSRC[idx] = futureSRC[0]
                if any(self.EESS.underSRC):
                    self.underSRC[idx] = 1
                if any(self.PH.outOfNormalBounds):
                    self.outOfNormalBounds[idx] = 1



