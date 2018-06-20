# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

#imports
from GBSModel.ThermalEnergyStorage import ThermalEnergyStorage
import os
import sys
import importlib.util

class ThermalEnergyStorageSystem:
    def __init__(self, tesIDS, tesT, tesStates, timeStep, tesDescriptor, tesDispatch):
        '''
        Constructor used for intialization of all Thermal Energy Storage units in this Thermal Energy Storage System.
        :param tesIDS:
        :param tesT:
        :param tesStates:
        :param timeStep:
        :param tesDescriptor:
        :param tesDispatch:
        '''
        # check to make sure same length data coming in
        if not len(tesIDS) == len(tesT) == len(tesStates) == len(tesDescriptor):
            raise ValueError('The length tesIDS, tesSOC, tesStates and tesDescriptor inputs to '
                             'ThermalEnergyStorageSystem must be equal.')

        # ************ TESS variables**********************
        # List of EES and their respective IDs
        self.thermalEnergyStorageUnits = []
        self.tesIDs = tesIDS

        # total power and energy capacities
        self.tesPInMax = 0
        self.tesPOutMax = 0
        self.tesEMax = 0

        # tes dispatch
        self.outOfBounds = []  # operating above max charging or discharging real power

        # Operational data
        self.tesT = list(tesT)
        self.tesStates = list(tesStates)
        self.tesPinAvail = []
        self.tesPoutAvail = []
        self.tesPloss = []
        self.tesP = [0] * len(self.tesT)

        # Populate the list of tes with tes objects
        # TODO: consider leaving values at tes level, not bringing them to this level if not necessary
        for idx, tesID in enumerate(tesIDS):
            # Initialize tes
            self.thermalEnergyStorageUnits.append(ThermalEnergyStorage(tesID, tesT[idx], tesStates[idx], timeStep, tesDescriptor[idx]))

            # Initial operating values
            self.tesPinAvail.append(self.thermalEnergyStorageUnits[idx].tesPinAvail)
            self.tesPoutAvail.append(self.thermalEnergyStorageUnits[idx].tesPoutAvail)
            self.tesPloss.append(self.thermalEnergyStorageUnits[idx].tesPloss)
            self.outOfBounds.append(self.thermalEnergyStorageUnits[idx].outOfBoundsReal)

            # total power and energy capacities
            self.tesPInMax += self.thermalEnergyStorageUnits[idx].tesPInMax
            self.tesPOutMax += self.thermalEnergyStorageUnits[idx].tesPOutMax
            self.tesEMax += self.thermalEnergyStorageUnits[idx].tesEMax

        # import the dispatch scheme
        # split into path and filename
        modPath, modFile = os.path.split(tesDispatch)
        # if located in a different directory, add to sys path
        if len(modPath) != 0:
            sys.path.append(modPath)
        # split extension off of file
        modFileName, modFileExt = os.path.splitext(modFile)
        # import module
        dispatchModule = importlib.import_module(modFileName)
        self.tesDispatch = dispatchModule.tesDispatch

    def runTesDispatch(self, newP):
        self.tesDispatch(self, newP)
        # check the operating conditions of tes, update counters
        for idx, tes in enumerate(self.thermalEnergyStorageUnits):
            tes.checkOperatingConditions()
            self.tesP[idx] = tes.tesP
            self.tesT[idx] = tes.tesT
            self.tesStates[idx] = tes.tesState
            self.tesPinAvail[idx] = tes.tesPinAvail
            self.tesPoutAvail[idx] = tes.tesPoutAvail
            self.tesPloss[idx] = tes.tesPloss
            self.outOfBounds[idx] = tes.outOfBounds