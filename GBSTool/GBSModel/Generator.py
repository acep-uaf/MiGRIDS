# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup
from GBSAnalyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve


class Generator:
    '''
    Generator class: contains all necessary information for a single generator. Multiple generators are aggregated in a
    Powerhouse object (see Powerhouse.py), which further is aggregated in the SystemOperations object (see
    SystemOperations.py).
    '''

    # Constructor
    def __init__(self, genID, genP, genQ, genState, genDescriptor):
        '''
        Constructor used for intialization of generator fleet in Powerhouse class.

        :param genID: internal id used in Powerhouse for tracking generator objects. *type int*
        :var genName: name given in genDescriptor, added here for object traceability. *type string*
        :var genP: the current real power level, units: kW. *type float*
        :var genQ: the current reactive power level, units: kvar. *type float*
        :var genState: the current operating state, 0 - off, 1 - running, 2 - online.
        :var genPMax: Generator real power nameplate capacity, units: kW. *type float*
        :var genQMax: Generator reactive power nameplate capacity, units: kvar. *type float*
        :var genPAvail: De-rating or nameplate real power capacity, current level, units: kW. *type float*
        :var genPMin: Minimum optimal loading, real power, units: kW. *type float*
        :var genRunTimeMin: Minimum run time, units: s. *type float*
        :var genStartTime: Time to start generator, units: s. *type int*
        :var genFuelCurve: Fuel curve, tuples of [kW, kg/s]. *type list(float,float)
        :var genRunTimeAct: Generator run time since last start [s]. *type int*
        :var genRunTimeTot: Generator cummulative run time since model start [s]. *type int*
        :
        '''

        # Generator resources
        # TODO: delete commented out variables that are set elsewhere in __init__
        #self.genID = None
        #self.genName = None  # This should come from the genDescriptor file and is merely used to trace back to that
        #self.genP = 0  # Current real power level [kW]
        #self.genQ = 0  # Current reactive power level [kvar]
        #self.genState = 0  # Generator operating state [dimensionless, index]. See docs for key.
        #self.genPMax = 0  # Nameplate capacity [kW]
        self.genQMax = 0  # Nameplate capacity [kvar]
        # TODO: default to PMax?
        self.genPAvail = 0  # De-rating or nameplate capacity [kW]
        self.genQAvail = 0  # De-rating or nameplate capacity [kvar]
        #self.genPMin = 0  # Minimum optimal loading [kW]
        #self.genRunTimeMin = 0  # Minimum run time [s] TODO: add 'Time' to naming convention
        #self.genStartTime = 0  # Time to start generator [s]
        #self.genFuelCurve = []  # Fuel curve, tuples of [kW, kg/s]

        self.genRunTimeAct = 0  # Run time since last start [s]
        self.genRunTimeTot = 0  # Cummulative run time since model start [s]

        """
        :param genID: integer for identification of object within Powerhouse list of generators.
        :param genP: initial real power level.
        :param genQ: initial reactive power level.
        :param genDescriptor: relative path and file name of genDescriptor-file used to populate static information.
        """

        # Write initial values to internal variables.
        self.genID = genID
        self.genP = genP
        self.genQ = genQ
        self.genState = genState
        # initiate operating condition flags and timers
        self.overLimitFlag = False # indicates when the generator is operating above the upperLimit (see genDescriptor.xml)
        self.underLimitFlag = False # indicates when the generator is operating below the lowerLimit (see genDescriptor.xml)
        # an energy counter that keeps track of how much the generator is operating above the upperNormalLoadingLimit
        # (see genDescriptor.xml)
        self.overNormalLoadingCounter = 0
        self.overNormalLoadingFlag = False # indicates when the generator is operating above upperNormalLoadingLimit
        self.underMolTimer = 0 # an energy timer that keeps track of how much the generator operates below (units kWs)
        self.underMolFlag = False # indicates
        genDescriptorParser(self, genDescriptor)


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
        self.genPMax = float(genSoup.POutMaxPa.get('value'))
        self.genPMin = float(genSoup.mol.get('value')) * self.genPMax
        self.genRunTimeMin = float(genSoup.minRunTime.get('value'))
        self.genStartTime = float(genSoup.startTime.get('value'))
        self.genStartCost =  float(genSoup.startCost.get('value'))
        self.genMol = float(genSoup.mol.get('value'))
        self.genMolLimit = float(genSoup.molLimit.get('value'))
        self.genMolTime = float(genSoup.molTime.get('value'))
        self.genUpperNormalLoading = float(genSoup.upperNormalLoading.get('value'))
        self.genUpperNormalLoadingTime = float(genSoup.upperNormalLoadingTime.get('value'))
        self.genLowerLimit = float(genSoup.lowerLimit.get('value'))
        self.genUpperLimit = float(genSoup.upperLimit.get('value'))

        # TODO: add upperNormalLimit, upperNormalLimitTime, molTime,

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

    def checkOperatingConditions(self):
        """
        Checks if the generator is operating within defined bounds. Otherwise, triggers the respective (cummulative
            energy) timers.

        :return:
        """
        # TODO: implement this, might include adding additional class-wide variables.

        # Check overload condition
        # is it over the normal operating threshold? (eg 90% full capacity), then initiate energy counter
        # is it over capacity? then immediatly trigger a flag

        # Check MOL condition
        # is it under MOL? then initiate energy counter

        # Check minimum runtime condition
        # decrement min runtime counter after initially bringing online]

        # is timer




