# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)
from bisect import bisect_left
from bs4 import BeautifulSoup as Soup
import sys
sys.path.append('../')
from GBSAnalyzer.CurveAssemblers.esLossMapAssembler import esLossMap
from GBSInputHandler.readXmlTag import readXmlTag
import numpy as np

class ElectricalEnergyStorage:
    '''
        Electrical Storage class: contains all necessary information for a single electrical storage unit. Multiple
        electrical storage units can be aggregated in an Electrical Storage System object (see
        ElectricalStorageSystem.py), which further is aggregated in the SystemOperations object (see
        SystemOperations.py).
        '''
    # Constructor
    def __init__(self, eesID, eesP, eesQ, eesSOC, eesState, eesSRC, timestep, eesDescriptor):
        """
        Constructor used for intialization of an Energy Storage unit in Energy Storage System class.
        :param eesID: integer for identification of object within Energy Storage System list of ees units.
        :param eesP: initial real power level.
        :param eesQ: initial reactive power level.
        :param eesSOC: initial state of charge.
        :param eesState: the current operating state, 0 - off, 1 - starting, 2 - online.
        :param eesSRC: the amount of spinning reserve capacity that the EES must be able to supply, in addition to active discharge.
        :param eesDescriptor: relative path and file name of eesDescriptor-file used to populate static information.
        """
        # manage run time timers
        self.eesRunTimeAct = 0
        self.eesRunTimeTot = 0
        self.eesStartTimeAct = 0

        # write initial values to internal variables
        self.eesID = eesID  # internal id used in Powerhouse for tracking generator objects. *type int*
        self.eesP = eesP  # Current real power level [kW]
        self.eesQ = eesQ  # Current reactive power level [kvar]
        self.eesSOC = eesSOC # Current state of charge in pu
        self.eesState = eesState  # Generator operating state [dimensionless, index]. See docs for key.
        self.eesSRC = eesSRC # the amount of SRC that the ess needs to be able to provide
        self.timeStep = timestep  # the time step used in the simulation in seconds

        # out of bounds operation flags
        self.underSRC = False # indicates when ees cannot supply required src

        # run the descriptor parser file to grab information from the descriptor file for this unit
        self.eesDescriptorParser(eesDescriptor)

        # update eesPAvail and eesQAvail depending on essState
        if eesState == 2:
            # TODO: change p available to take into account soc
            self.eesPAvail = self.eesPMax  # P available is the how much power is avialable online. P max if online, 0 otherwise
            self.genQAvail = self.genQMax
        else:
            self.genPAvail = 0
            self.genQAvail = 0

    # energy storage descriptor parser
    def eesDescriptorParser(self, eesDescriptor):
        """
        Reads the data from a given eesDescriptor file and uses the information given to populate the
        respective internal variables.

        :param eesDescriptor: relative path and file name of eesDescriptor.xml-file that is used to populate static
        information

        :return:
        """
        # read xml file
        eesDescriptorFile = open(eesDescriptor, "r")
        eesDescriptorXml = eesDescriptorFile.read()
        eesDescriptorFile.close()
        eesSoup = Soup(eesDescriptorXml, "xml")

        # Dig through the tree for the required data
        self.eesName = eesSoup.component.get('name')
        self.eesPOutMax = float(eesSoup.POutMaxPa.get('value'))  # max discharging power
        self.eesPInMax = float(eesSoup.PInMaxPa.get('value'))  # max charging power
        self.eesQOutMax = float(eesSoup.QOutMaxPa.get('value'))  # max discharging power reactive
        self.eesQInMax = float(eesSoup.QInMaxPa.get('value'))  # max charging power reactive
        # TODO: add the effect of charge/discharge rate on capacity. Possibly add something similar to the LossMap
        self.eesEMax = float(eesSoup.energyCapacity.get('value')) # the maximum energy capacity of the EES in kWs
        # the amount of time in seconds that the EES must be able to discharge for at current level of SRC being provided
        self.eesSrcTime = float(eesSoup.eesSrcTime.get('value'))
        # 'eesDispatchTime' is the minimum amount of time that the ESS must be able to supply the load for in order to
        # be considered as an active discharge option in the diesel schedule.
        self.eesDispatchTime = float(eesSoup.eesDispatchTime.get('value'))
        # In order to use the consider the equivalent fuel efficiency of dishcarging the ESS to allow running a smaller
        # diesel generator, an equivalent fuel consumption of the ESS must be calculated in kg/kWh. This is done by calculating
        # how much diesel fuel went into charging the ESS to it's current level. Divide the number of kg by the state of
        # charge to get the fuel consumption of using the energy storage.
        # 'prevEesTime' is how far back that is used to assess what percentage of the current ESS charge came from
        # the diesel generator. This is used in the dispatch schedule to determine the cost of discharging the ESS to supply
        # the load for peak shaving or load leveling purposes.
        self.prevEesTime = float(eesSoup.prevEesTime.get('value'))
        # 'eesCost' is the cost of discharging the ESS that is above the fuel cost that went into charging it. It is
        # stated as a fuel consumption per kWh, kg/kWh. It is added to the effective fuel consumption of discharging the
        # ESS resulting from chargning it with the diesel generators. The cost is used to account for non-fuel costs of
        # discharging the ESS including maintenance and lifetime costs. Units are kg/kWh.
        self.eesCost = float(eesSoup.eesCost.get('value'))
        # 'essChargeRate' is the fraction of power that it would take to fully charge or discharge the ESS that is the
        # maximum charge or discharge power. This creates charging and discharging curves that exponentially approach full
        # and zero charge.
        self.eesChargeRate = float(eesSoup.chargeRate.get('value'))

        # handle the loss map interpolation
        # 'lossMap' describes the loss experienced by the energy storage system for each state of power and energy.
        # they are described by the tuples 'pPu' for power, 'ePu' for the state of charge, 'tempAmb' for the ambient
        # (outside) temperature and 'lossRate' for the loss. Units for power are P.U. of nameplate power capacity. Positive values
        # of power are used for discharging and negative values for charging. Units for 'ePu' are P.U. nameplate energy
        # capacity. It should be between 0 and 1. 'loss' should include all losses including secondary systems. Units for
        # 'loss' are kW.
        # initiate loss map class
        eesLM = esLossMap()
        pPu = np.array(readXmlTag(eesDescriptor,['lossMap','pPu'],'value','', 'float'))
        ePu = readXmlTag(eesDescriptor, ['lossMap', 'ePu'], 'value','',  'float')
        lossPu = readXmlTag(eesDescriptor, ['lossMap', 'loss'], 'value','',  'float')
        tempAmb = readXmlTag(eesDescriptor, ['lossMap', 'tempAmb'], 'value','',  'float')

        # convert per unit power to power
        P = np.array(pPu)
        P[P>0] = P[P>0]*self.eesPOutMax
        P[P<0] = P[P<0]*self.eesPInMax
        #convert per unit energy to energy
        E = np.array(ePu)*self.eesEMax
        # convert pu loss to power
        L = np.abs(np.array(lossPu) * P)

        lossMapDataPoints = []
        for idx, item in enumerate(pPu):
            lossMapDataPoints.append((float(P[idx]), float(E[idx]), float(L[idx]), float(tempAmb[idx])))

        eesLM.lossMapDataPoints = lossMapDataPoints
        eesLM.pInMax = self.eesPInMax
        eesLM.pOutMax = self.eesPOutMax
        eesLM.eMax = self.eesEMax
        # check inputs
        eesLM.checkInputs()
        # perform the linear interpolation between points
        eesLM.linearInterpolation(self.eesChargeRate, eStep = 3600*2)

        self.eesLossMapP = eesLM.P
        self.eesLossMapE = eesLM.E
        self.eesLossMapTemp = eesLM.Temp
        self.eesLossMapLoss = eesLM.loss
        self.eesmaxDischTime = eesLM.maxDischTime
        # 'useLossMap' is a bool value that indicates whether or not use the lossMap in the simulation.
        self.eesUseLossMap = bool(eesSoup.useLossMap.get('value'))

# todo: finish this, handle 2D vs 3D if temperature is considered.
    def getLossDischargeTimes(self):
        if self.eesUseLossMap:
            # create a parallel matrix to the lossMap with the amount of time it is possible to discharge at each power for
            # taking into account losses
            for idxE, E in enumerate(self.eesLossMapE): # for every soc
                for idxP, P in enumerate(self.eesLossMapP): # for every power
                    for idxTemp, Temp in enumerate(self.essLossMapTemp):
                        if P > 0: # if discharging
                            # the maximum amount of time that can discharge for at this power
                            self.eesLossDischargeTimes[idxP,idxE] = max([E/(P+self.eesLossMapLoss) - 1/self.eesChargeRate,0])
                        else:
                            # the maximum amount of time that can be discharged at
                            self.eesLossDischargeTimes[idxP,idxE] = max([(self.eesEMax - E)/(-P+self.eesLossMapLoss) - 1/self.eesChargeRate,0])

        else:
            self.eesLossDischargeTimes = []

    def checkOperatingConditions(self):
        """
        Checks if the ees is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        if self.eesState == 2: # if running online
            # maximum available power is the minimum of the:
            # - stored energy (in kWs) divided by the number of seconds in a timestep
            # - maximum rated power
            self.eesPAvail = min([self.eesPOutMax,self.eesSOC*self.eesEMax/self.timeStep])
            self.eesQAvail = self.eesQOutMax # available reactive power is not directly tied to the state of charge
            # TODO: make sure enough power and soc for SRC, ...
            # check enough power capability left to supply SRC
            if self.eesSRC > (self.eesPAvail - self.eesP): # if required SRC is greater than the remaining available power
                self.underSRC = True

            # check that there is enough capacity left to supply SRC
            self.eesRunTimeAct += self.timeStep
            self.eesRunTimeTot += self.timeStep
        elif self.eesState == 1: # if starting up
            self.eesPAvail = 0 # not available to produce power yet
            self.eesQAvail = 0
            self.eesStartTimeAct += self.timeStep
            self.eesRunTimeAct = 0 # reset run time counter
        else: # if off
            # no power available and reset counters
            self.eesPAvail = 0
            self.eesQAvail = 0
            self.eesStartTimeAct = 0
            self.eesRunTimeAct = 0

    # this finds the available discharge power given
    def findPchAvail(self, duration):
        if self.eesUseLossMap == False: # if don't use loss map
            # the available charging power is the minimum of how much the SOC will support and the maximum rated power
            # eesChargeRate is limits the power as based on SOC
            self.eesPchAvail = min([self.eesPMax,self.eesChargeRate*self.eesEMax*self.eesSOC/self.timeStep])
        else: # if use the loss map
            # find the index of the closest P and E value on the loss map
            # bisect left gives the index of the last list item to not be over the number being searched for. it is faster than using min
            Pind = bisect_left(self.eesLossMap)

            # this finds the associated fuel consumption to the scheduled load for this combination
            fuelCons.append(FCcons[bisect_left(FCpower, scheduledLoad)])