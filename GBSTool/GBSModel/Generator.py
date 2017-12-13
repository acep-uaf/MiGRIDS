# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup

class Generator:


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

    # TODO: genFuelUse - figure out format and use and tie in GBSAnalyzer.genFuelCurveEstimator

    # Constructor
    def __init__(self, genID, genP, genQ, genDescriptor):
        """
        Constructor used for intialization of generator fleet in Powerhouse class

        :param genID: integer for identification of object within Powerhouse list of generators
        :param genP: initial real power level
        :param genQ: initial reactive power level
        :param genDescriptor: relative path and file name of genDescriptor.xml-file that is used to populate static information
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

        :param genDescriptor:
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
        # TODO: deal with fuel curve estimations
        self.genPMax = float(genSoup.POutMaxPa.get('value'))
        self.genPMin = float(genSoup.mol.get('value')) * self.genPMax
        self.genRunTimeMin = float(genSoup.minRunTime.get('value'))
        self.genStartTime = float(genSoup.startTime.get('value'))


