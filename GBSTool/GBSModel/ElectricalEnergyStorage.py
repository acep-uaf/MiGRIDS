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
    def __init__(self, eesID, eesSOC, eesState, timestep, eesDescriptor):
        """
        Constructor used for intialization of an Energy Storage unit in Energy Storage System class.
        :param eesID: integer for identification of object within Energy Storage System list of ees units.
        :param eesSOC: initial state of charge.
        :param eesState: the current operating state, 0 - off, 1 - starting, 2 - online.
        :param eesDescriptor: relative path and file name of eesDescriptor-file used to populate static information.
        """
        # manage run time timers
        self.eesRunTimeAct = 0
        self.eesRunTimeTot = 0
        self.eesStartTimeAct = 0

        # write initial values to internal variables
        self.eesID = eesID  # internal id used in Powerhouse for tracking generator objects. *type int*
        self.eesSOC = eesSOC # Current state of charge in pu
        self.eesState = eesState  # Generator operating state [dimensionless, index]. See docs for key.
        self.timeStep = timestep  # the time step used in the simulation in seconds


        # run the descriptor parser file to grab information from the descriptor file for this unit
        self.eesDescriptorParser(eesDescriptor)

        # this sets the amount of SRC that the ess needs to be able to provide and the calculates the minimum ees stored
        # energy that must be maintained. run self.setSRC to set the SRC.
        self.eesSRC = 0

        # this updates the power availble from this ees to be used in scheduling generating units
        self.updatePScheduleMax()

        # these values will be set when checkOperatingConditions is run
        self.eesP = 0
        self.eesQ = 0
        self.eesPinAvail = 0
        self.eesPinAvail_1 = 0
        self.eesPsrcAvail = 0
        self.eesQinAvail = self.eesQInMax
        self.eesPoutAvail = 0
        self.eesQoutAvail = self.eesQOutMax
        self.underSRC = 0
        self.outOfBoundsReal = 0
        self.outOfBoundsReactive = 0
        self.eesPoutAvailOverSrc = 0
        self.eesPoutAvailOverSrc_1 = 0
        self.eesPloss = 0

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
        # 'eesPinAvail_1_time' is used to find the maximum power that the EES can charge for 'eesPinAvail_1_time'
        # amount of time before being fully charged.  Units are in seconds. Default is 300 s (5 min).
        self.eesPinAvail_1_time = float(eesSoup.eesPinAvail_1_time.get('value'))
        # 'eesPoutAvail_1_time' is used to find the maximum power that the EES can discharge for 'eesPoutAvail_1_time'
        # amount of time before going below the required SRC SOC.  Units are in seconds. Default is 300 s (5 min).
        self.eesPoutAvail_1_time = float(eesSoup.eesPoutAvail_1_time.get('value'))
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
        # TODO: remove *2, this is for testing purposes
        # perform the linear interpolation between points, with an energy step every 1 kWh (3600 seconds)
        eesLM.linearInterpolation(self.eesChargeRate, eStep = 3600*2)

        self.eesLossMapP = eesLM.P
        # save the index of where the power vector is zero. This is used to speed up run time calculations
        self.eesLossMapPZeroInd = (np.abs(self.eesLossMapP)).argmin()
        self.eesLossMapE = eesLM.E
        self.eesLossMapTemp = eesLM.Temp
        self.eesLossMapLoss = eesLM.loss
        self.eesmaxDischTime = eesLM.maxDischTime
        self.eesNextBinTime = eesLM.nextBinTime
        # 'useLossMap' is a bool value that indicates whether or not use the lossMap in the simulation.
        self.eesUseLossMap = bool(eesSoup.useLossMap.get('value'))

    def checkOperatingConditions(self):
        """
        Checks if the ees is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        if self.eesState == 2: # if running online
            # find the loss at the current power and SOC state
            self.eesPloss = self.findLoss(self.eesP,self.timeStep)
            # update the SOC
            self.eesSOC = min([max([self.eesSOC - (self.eesP + self.eesPloss)*self.timeStep/self.eesEMax,0]),1])
            # find the available real power (reactive is set to max)
            self.eesPinAvail = self.findPchAvail(self.timeStep)
            self.eesPoutAvail = self.findPdisAvail(self.timeStep, 0, 0)

            ''' calculate these as needed in dispatch 
            # given the SRC required from the EES, find the maximum power available for a minimum of 1 timestep
            
            self.eesPinAvail_1 = self.findPchAvail(self.eesPinAvail_1_time)
            self.eesQinAvail = self.eesQInMax  # reactive power is not strictly tied to state of charge
            # the maximum currently available discharge power for 1 timestep
            
            self.eesQoutAvail = self.eesQOutMax # reactive power is not strictly tied to state of charge

            # The max power available while reserving enough capacity for SRC, this will return a negative value if not
            # enough capacity left for SRC.
            self.eesPoutAvailOverSrc = self.findPdisAvail(self.timeStep,self.eesSRC,self.eesMinSrcE)
            self.eesPoutAvailOverSrc_1 = self.findPdisAvail(self.eesPoutAvail_1_time, self.eesSRC, self.eesMinSrcE)
            '''
            # check if not enough SRC
            if self.eesPoutAvailOverSrc < 0:
                self.underSRC = True
            else:
                self.underSRC = False

            # check to make sure the current power output or input is not greater than the maximum allowed.
            if (self.eesP > self.eesPoutAvail) | (self.eesP < -self.eesPinAvail):
                self.outOfBoundsReal = True
            else:
                self.outOfBoundsReal = False
            if (self.eesQ > self.eesQoutAvail) | (self.eesQ < -self.eesQinAvail):
                self.outOfBoundsReactive = True
            else:
                self.outOfBoundsReactive = False

            self.eesRunTimeAct += self.timeStep
            self.eesRunTimeTot += self.timeStep
        elif self.eesState == 1: # if starting up
            self.eesPinAvail = 0 # not available to produce power yet
            self.eesPinAvail_1 = 0
            self.eesQinAvail = 0
            self.eesPoutAvail = 0  # not available to produce power yet
            self.eesQoutAvail = 0
            self.eesPoutAvailOverSrc = 0
            self.eesPoutAvailOverSrc_1 = 0
            self.eesStartTimeAct += self.timeStep
            self.eesRunTimeAct = 0 # reset run time counter
            self.underSRC = False
            self.outOfBoundsReal = False
            self.outOfBoundsReactive = False
        else: # if off
            # no power available and reset counters
            self.eesPinAvail = 0  # not available to produce power yet
            self.eesPinAvail_1 = 0
            self.eesQinAvail = 0
            self.eesPoutAvail = 0  # not available to produce power yet
            self.eesQoutAvail = 0
            self.eesPoutAvailOverSrc = 0
            self.eesPoutAvailOverSrc_1 = 0
            self.eesStartTimeAct = 0
            self.eesRunTimeAct = 0
            self.underSRC = False
            self.outOfBoundsReal = False
            self.outOfBoundsReactive = False

    # this finds the available charging power
    # duration is the duration that needs to be able to charge at that power for
    def findPchAvail(self, duration):
        # get the index of the closest E from the loss map
        eInd = np.searchsorted(self.eesLossMapE,self.eesSOC*self.eesEMax,side='left')
        # get the searchable array for charging power (negative) the discharge times for this are already sorted in
        # increasing order, so do not need to be sorted
        ChTimeSorted = self.eesmaxDischTime[:self.eesLossMapPZeroInd,eInd]
        # get the index of the closest discharge time to duration
        # need to reverse the order of discharge times to get
        dInd  = np.searchsorted(ChTimeSorted,duration,side='right')
        # the available charging power corresponds to the
        return -self.eesLossMapP[dInd]

    # this finds the available discharge power
    # duration is the duration that needs to be able to discharge at that power for
    # kWreserved is the amount of charging power that is already spoken for
    # kWhReserved is the amount of energy that is already spoken for, for example for spinning reserve.  This must also
    # take into account the losses involved. For example, if for spinning reserve need to be able to discharge at 100 kW
    # for 180 sec, and at the current SOC this would result in 500 kWs of losses, then kWsReserved would be 18,500 kWs.
    # findLoss is a bool value. if True, the associated loss will be calculated for discharging at that power
    def findPdisAvail(self, duration, kWReserved, kWsReserved):
        # get the index of the closest E from the loss map to the current energy state minus the reserved energy.
        # Subtracting the kWsReserved from the current SOC is not the most accurate way to do this, but it is a good
        # estimate. Ideally would search between current SOC down to kWsReserved, instead of of (current SOC -
        # kWsReserved) down to zero. However, this would not allow precalculating the matrix eesmaxDischTime.
        # TODO remove once other works
        eInd = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax - kWsReserved, side='left')

        # index of the energy closest to the current energy level stored
        eIndHere = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax, side='left')
        # index of the energy required for SRC
        # TODO: consider saving this index to avoid this search
        eIndSrc = np.searchsorted(self.eesLossMapE, kWsReserved, side='left')
        # get the searchable array for discharging power (positive). The discharge time is the difference between the
        # time to fully discharge the current energy bin and the time to fully discharge the energy bin required for
        # spinning reserve
        DisTimeSorted = self.eesmaxDischTime[self.eesLossMapPZeroInd + 1:, eIndHere] - \
                        self.eesmaxDischTime[self.eesLossMapPZeroInd + 1:, eIndSrc]
        # the discharge times for this are sorted in
        # decreasing order, so needs to be reversed
        DisTimeSorted = DisTimeSorted[::-1]
        dInd = np.searchsorted(DisTimeSorted, duration, side='right')
        # the index is from the back of the array, since was from a reversed array.
        # the maximum discharging power is the minimum of the power allowed to reserve the required capacity and the
        # difference between the maximum power and the reserved power in order to keep that power capability reserved.
        return min([self.eesLossMapP[-(dInd + 1)], self.eesPOutMax - kWReserved])

        ''' # TODO: remove this once determine other working
        # get the searchable array for discharging power (positive) the discharge times for this are sorted in
        # decreasing order, so needs to be reversed
        DisTimeSorted = self.eesmaxDischTime[self.eesLossMapPZeroInd+1:, eInd]
        DisTimeSorted = DisTimeSorted[::-1]
        # get the index of the closest discharge time to duration
        # need to reverse the order of discharge times to get
        dInd = np.searchsorted(DisTimeSorted, duration, side='right')

        # the index is from the back of the array, since was from a reversed array.
        return self.eesLossMapP[-(dInd+1)] - kWReserved

        '''
    # findLoss returns the expected loss in kWs given a specific power and duration
    # P is the power expected to discharge at
    # duration is the time expected to discharge at P for
    def findLoss(self,P,duration):

        if P > 0: # if discharging
            # if the power is within the chargeRate and max discharge bounds
            #if (P <= self.eesSOC * self.eesEMax * self.eesChargeRate)  & P <= self.eesPOutMax:
                # get the index of the closest E from the loss map to the current energy state minus the reserved energy
                eInd = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax, side='left')
                # get index of closest P
                pInd = np.searchsorted(self.eesLossMapP, P, side = 'left')
                # create a cumulative sum of discharge times
                # since discharging, the stored energy will be going down, thus reverse the order
                times = self.eesNextBinTime[pInd,:eInd]
                times = times[::-1]
                cumSumTime = np.cumsum(times)
                # get the index closest to the duration required
                dInd = np.searchsorted(cumSumTime,duration)
                return sum(self.eesLossMapLoss[pInd,(eInd-dInd-1):eInd])


        elif P < 0: # if charging
            # if the power is within the chargeRate and max discharge bounds
           # if (P >= (self.eesSOC - 1)*self.eesEMax  * self.eesChargeRate) & P >= -self.eesPInMax:
                # get the index of the closest E from the loss map to the current energy state minus the reserved energy
                eInd = np.searchsorted(self.eesLossMapE, self.eesSOC * self.eesEMax, side='left')
                # get index of closest P
                pInd = np.searchsorted(self.eesLossMapP, P, side='left')
                # create a cumulative sum of discharge times
                cumSumTime = np.cumsum(self.eesNextBinTime[pInd, eInd:])
                # get the index closest to the duration required
                dInd = np.searchsorted(cumSumTime, duration)
                return sum(self.eesLossMapLoss[pInd, eInd:(eInd + dInd+1)])

        else: # if not doing anything
            return 0

    # this will set the required SRC and find the minimum SOC that the ees must stay above to be able to supply the
    # required SRC
    def setSRC(self, SRC):
        # set the required SRC in kW
        self.eesSRC = SRC
        # get index of closest P to SRC
        pInd = np.searchsorted(self.eesLossMapP, SRC, side='left')
        # get the index of the closest max discharge time to the required SRC time
        eInd = np.searchsorted(self.eesmaxDischTime[pInd, :], self.eesSrcTime, side='left')
        # set the required energy stored in the ees to supply the SRC, in kWs
        self.eesMinSrcE = self.eesLossMapE[eInd]

    # this finds the available SRC given the current power
    def updateSrcAvail(self):
        useP = max([self.eesP,0]) # only take into account discharging power
        self.eesPsrcAvail = self.findPdisAvail(self.eesSrcTime, useP, useP*self.timeStep)

    # this finds the power this ees is capable of being scheduled for.
    def updatePScheduleMax(self):
        self.eesPScheduleMax = self.findPdisAvail(self.eesDispatchTime, self.eesSRC, self.eesMinSrcE)