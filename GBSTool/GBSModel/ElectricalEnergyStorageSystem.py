# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 8, 2018
# License: MIT License (see LICENSE file of this package for more information)

from ElectricalEnergyStorage import ElectricalEnergyStorage
import itertools
import sys
import numpy as np
sys.path.append('../')
import importlib.util
# import EESSDispatch

class ElectricalEnergyStorageSystem:

    def __init__(self, eesIDS, eesP, eesQ, eesSOC, eesStates, eesSRC, timeStep, eesDescriptor, eesDispatch):
        """
        Constructor used for intialization of all Energy Storage units in this Energy Storage System.
        :param eesIDS: list of integers for identification of Energy Storage units.
        :param eesP: list of initial real power level.
        :param eesQ: list of initial reactive power level.
        :param eesSOC: list of initial state of charge.
        :param eesState: list of the initial operating state, 0 - off, 1 - starting, 2 - online.
        :param eesSRC: list of the amount of spinning reserve capacity that the EESs must be able to supply, in addition
        to active discharge.
        :param eesDescriptor: list of relative path and file name of eesDescriptor-files used to populate static information.
        :param eesDispatch: Is the path and filename of the dispatch class used to dispatch the energy storage units.
        """
        # check to make sure same length data coming in
        if not len(eesIDS) == len(eesP) == len(eesQ) == len(eesSOC)==len(eesStates)==len(eesSRC)==len(eesDescriptor):
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
        self.eesP = list(eesP)
        self.eesQ = list(eesQ)
        self.eesSOC = list(eesSOC)
        self.eesStates = list(eesStates)
        self.eesSRC = list(eesSRC)
        self.eesPinAvail = []
        self.eesPinAvail_1 = []
        self.eesQinAvail = []
        self.eesPoutAvail = []
        self.eesQoutAvail = []
        self.eesPoutAvailOverSrc = []
        self.eesPoutAvailOverSrc_1 = []

        # Populate the list of ees with ees objects
        # TODO: consider leaving values at ees level, not bringing them to this level if not necessary
        for idx, eesID in enumerate(eesIDS):
            # Initialize EES
            self.electricalEnergyStorageUnits.append(ElectricalEnergyStorage(eesID, eesP[idx], eesQ[idx], eesSOC[idx], eesStates[idx], eesSRC[idx], timeStep, eesDescriptor[idx]))

            # Initial operating values
            self.eesPinAvail.append(self.electricalEnergyStorageUnits[idx].eesPinAvail)
            self.eesQinAvail.append(self.electricalEnergyStorageUnits[idx].eesQinAvail)
            self.eesPoutAvail.append(self.electricalEnergyStorageUnits[idx].eesPoutAvail)
            self.eesQoutAvail.append(self.electricalEnergyStorageUnits[idx].eesQoutAvail)
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

        # import the dispatch scheme
        # TODO: test this
        spec = importlib.util.spec_from_file_location("eesDispatch", eesDispatch)
        eesDispatch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eesDispatch)

