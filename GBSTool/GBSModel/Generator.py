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

    :param genID: internal id used in Powerhouse for tracking generator objects. *type int*
    :var genName: name given in genDescriptor, added here for object traceability. *type string*
    :var genP: the current real power level, units: kW. *type float*
    :var genQ: the current reactive power level, units: kvar. *type float*
    :var genPMax: Generator real power nameplate capacity, units: kW. *type float*
    :var genQMax: Generator reactive power nameplate capacity, units: kvar. *type float*
    :var genPAvail: De-rating or nameplate real power capacity, current level, units: kW. *type float*
    :var genPMin: Minimum optimal loading, real power, units: kW. *type float*
    :var genRunTimeMin: Minimum run time, units: h. *type float*
    :var genStartTime: Time to start generator, units: min. *type int*

    :
    '''

    # Generator resources
    genID = None
    genName = None # This should come from the genDescriptor file and is merely used to trace back to that
    genP = 0  # Current real power level [kW]
    genQ = 0  # Current reactive power level [kvar]
    genPMax = 0  # Nameplate capacity [kW]
    genQMax = 0  # Nameplate capacity [kvar]
    genPAvail = 0   # De-rating or nameplate capacity [kW]
    genQAvail = 0  # De-rating or nameplate capacity [kvar]
    genPMin = 0  # Minimum optimal loading [kW]
    genRunTimeMin = 0  # Minimum run time [h] TODO: add 'Time' to naming covention
    genStartTime = 0  # Time to start generator [min]
    genFuelCurve = []  # Fuel curve, tuples of [kW, kg/s]

    # Constructor
    def __init__(self, genID, genP, genQ, genDescriptor):
        """
        Constructor used for intialization of generator fleet in Powerhouse class.

        :param genID: integer for identification of object within Powerhouse list of generators.
        :param genP: initial real power level.
        :param genQ: initial reactive power level.
        :param genDescriptor: relative path and file name of genDescriptor-file used to populate static information.

        """

        # Write initial values to internal variables.
        self.genID = genID
        self.genP = genP
        self.genQ = genQ
        genDescriptor(self, genDescriptor)


    # Generator descriptor parser
    def genDescriptorParser(self, genDescriptor):
        """
        Reads the data from a given genDescriptor file and uses the information given to populate the
        respective internal variables.

        :param genDescriptor: relative path and file name of genDescriptor.xml-file that is used to populate static
        information

        :return:
        """
        # TODO: Implement parser that populates the necessary variables based on the selected generator descriptor

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

        # Handle the fuel curve interpolation
        fuelCurvePPuInpt = genSoup.fuelCurve.pPu.get('value').split()
        fuelCurveMFInpt = genSoup.fuelCurve.massFlow.get('value').split()
        fuelCurveData = []
        for idx, item in enumerate(fuelCurvePPuInpt):
            fuelCurveData.append((self.genPMax * float(fuelCurvePPuInpt[idx]), float(fuelCurveMFInpt[idx])))
        genFC = GenFuelCurve()
        genFC.fuelCurveDataPoints = fuelCurveData
        genFC.genOverloadPMax = self.genPMax # TODO: consider making this something else.
        genFC.cubicSplineCurveEstimator()
        self.genFuelCurve = genFC.fuelCurve # TODO: consider making this the integer version.


