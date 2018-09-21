# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

import sys

from GBSModel.ElectricalEnergyStorage import ElectricalEnergyStorage

sys.path.append('../')
import importlib.util
import os
# import EESSDispatch

class ElectricalEnergyStorageSystem:

    def __init__(self, eesIDS, eesSOC, eesStates, timeStep, eesDescriptor, eesDispatch, timeSeriesLength):
        """
        Constructor used for intialization of all Energy Storage units in this Energy Storage System.
        :param eesIDS: list of integers for identification of Energy Storage units.
        :param eesSOC: list of initial state of charge.
        :param eesState: list of the initial operating state, 0 - off, 1 - starting, 2 - online.
        :param eesDescriptor: list of relative path and file name of eesDescriptor-files used to populate static information.
        :param eesDispatch: If a user defines their own dispatch, it is the path and filename of the dispatch class used
        to dispatch the energy storage units. Otherwise, it is the name of the dispatch filename included in the software
        package. Options include: eesDispatch1. The class name in the file must be 'eesDispatch'. It needs to run the function
        updateSrcAvail() for each energy storage unit, after assigning the power to eesP, to update the eesSrcAvail property.
        """
        # check to make sure same length data coming in
        if not len(eesIDS) == len(eesSOC)==len(eesStates)==len(eesDescriptor):
            raise ValueError('The length eesIDS, eesP, eesQ, eesSOC, eesStates,eesSRC and eesDescriptor inputs to '
                             'ElectricalEnergyStorage must be equal.')
        # ************ EESS variables**********************
        # List of EES and their respective IDs
        self.electricalEnergyStorageUnits = []
        self.eesIDs = eesIDS

        # total power and energy capacities
        self.eesPInMax = 0
        self.eesQInMax = 0
        self.eesPOutMax = 0
        self.eesQOutMax = 0
        self.eesEMax = 0

        # ees dispatch
        self.underSRC = [] # not enough capacity left to supply required SRC
        self.outOfBoundsReal = [] # operating above max charging or discharging real power
        self.outOfBoundsReactive = []  # operating above max charging or discharging reactive power

        # timers
        self.eesStartTimeAct = []
        self.eesRunTimeAct = []
        self.eesRunTimeTot = []

        # Operational data
        # TODO: remove what is not being used
        self.eesSOC = list(eesSOC)
        self.eesStates = list(eesStates)
        self.eesPinAvail = []
        self.eesPinAvail_1 = []
        self.eesQinAvail = []
        self.eesPoutAvail = []
        self.eesQoutAvail = []
        self.eesPsrcAvail = []
        self.eesPloss = []
        self.eesPoutAvailOverSrc = []
        self.eesPoutAvailOverSrc_1 = []
        self.eesPScheduleMax = [0]*len(self.eesSOC)
        self.eesP = [0] * len(self.eesSOC)
        self.eesQ = [0] * len(self.eesSOC)
        self.eesSRC = [0] * len(self.eesSOC)

        # Populate the list of ees with ees objects
        # TODO: consider leaving values at ees level, not bringing them to this level if not necessary
        for idx, eesID in enumerate(eesIDS):
            # Initialize EES
            self.electricalEnergyStorageUnits.append(ElectricalEnergyStorage(eesID, eesSOC[idx], eesStates[idx], timeStep, eesDescriptor[idx], timeSeriesLength))

            # Initial operating values
            self.eesPinAvail.append(self.electricalEnergyStorageUnits[idx].eesPinAvail)
            self.eesQinAvail.append(self.electricalEnergyStorageUnits[idx].eesQinAvail)
            self.eesPoutAvail.append(self.electricalEnergyStorageUnits[idx].eesPoutAvail)
            self.eesQoutAvail.append(self.electricalEnergyStorageUnits[idx].eesQoutAvail)
            self.eesPsrcAvail.append(self.electricalEnergyStorageUnits[idx].eesPsrcAvail)
            self.eesPloss.append(self.electricalEnergyStorageUnits[idx].eesPloss)
            self.eesPinAvail_1.append(self.electricalEnergyStorageUnits[idx].eesPinAvail)
            self.eesPoutAvailOverSrc.append(self.electricalEnergyStorageUnits[idx].eesPoutAvailOverSrc)
            self.eesPoutAvailOverSrc_1.append(self.electricalEnergyStorageUnits[idx].eesPoutAvailOverSrc_1)
            self.underSRC.append(self.electricalEnergyStorageUnits[idx].underSRC)
            self.outOfBoundsReal.append(self.electricalEnergyStorageUnits[idx].outOfBoundsReal)
            self.outOfBoundsReactive.append(self.electricalEnergyStorageUnits[idx].outOfBoundsReactive)

            # counters
            self.eesStartTimeAct.append(self.electricalEnergyStorageUnits[idx].eesStartTimeAct)
            self.eesRunTimeAct.append(self.electricalEnergyStorageUnits[idx].eesRunTimeAct)
            self.eesRunTimeTot.append(self.electricalEnergyStorageUnits[idx].eesRunTimeTot)

            # total power and energy capacities
            self.eesPInMax += self.electricalEnergyStorageUnits[idx].eesPInMax
            self.eesQInMax += self.electricalEnergyStorageUnits[idx].eesQInMax
            self.eesPOutMax += self.electricalEnergyStorageUnits[idx].eesPOutMax
            self.eesQOutMax += self.electricalEnergyStorageUnits[idx].eesQOutMax
            self.eesEMax += self.electricalEnergyStorageUnits[idx].eesEMax

        # import the dispatch scheme
        # split into path and filename
        modPath, modFile = os.path.split(eesDispatch)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        dispatchModule = importlib.import_module(modFileName)
        self.eesDispatch = dispatchModule.eesDispatch


    # this runs the ees dispatch schedule
    def runEesDispatch(self, newP, newQ, newSRC, tIndex):
        self.eesDispatch(self, newP, newQ, newSRC)
        # check the operating conditions of ees, update counters
        for idx, ees in enumerate(self.electricalEnergyStorageUnits):
            self.eesP[idx] = ees.eesP
            self.eesQ[idx] = ees.eesQ
            self.eesSOC[idx] = ees.eesSOC
            self.eesStates[idx] = ees.eesState
            self.eesSRC[idx] = ees.eesSRC
            self.eesPsrcAvail[idx] = ees.eesPsrcAvail
            self.eesPinAvail[idx] = ees.eesPinAvail
            self.eesPoutAvail[idx] = ees.eesPoutAvail
            self.eesQinAvail[idx] = ees.eesQinAvail
            self.eesQoutAvail[idx] = ees.eesQoutAvail
            self.eesPloss[idx] = ees.eesPloss
            self.underSRC[idx] = ees.underSRC
            self.outOfBoundsReal[idx] = ees.outOfBoundsReal
            self.outOfBoundsReactive[idx] = ees.outOfBoundsReactive

    # this finds the power each energy storage unit is capable of being scheduled for.
    def updateEesPScheduleMax(self):
        for idx, ees in enumerate(self.electricalEnergyStorageUnits):
            ees.updatePScheduleMax()
            self.eesPScheduleMax[idx] = ees.eesPScheduleMax

    # TODO: include scheduling (turning on and off of units). Need to have turn on and off times. What are reasons for
            # turning off in a simulation?