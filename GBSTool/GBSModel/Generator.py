# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# General imports
from bs4 import BeautifulSoup as Soup

class Generator:
    # Generator resources
    genID = None
    genP = 0
    genQ = 0
    genPMax = 0
    genQMax = 0
    genPAvail = 0
    genQAvail = 0

    # TODO: Implement constructor, etc.

    # __init__ Constructor used for intialization of generator fleet in Powerhouse class
    # Inputs:
    # genID - integer for identification of object within Powerhouse list of generators
    # genP - initial real power level
    # genQ - initial reactive power level
    # genDescriptor - relative path and file name of genDescriptor.xml-file that is used to populate static information
    def __init__(self, genID, genP, genQ, genDescriptor):
        # Write initial values to internal variables.
        self.genID = genID
        self.genP = genP
        self.genQ = genQ
        genDescriptor(self, genDescriptor)


    # Generator descriptor parser
    def genDescriptorParser(self, genDescriptor):
        # TODO: Implement parser that populates the necessary variables based on the selected generator descriptor

        # read xml file
        genDescriptorFile = open(genDescriptor, "r")
        genDescriptorXml = genDescriptorFile.read()
        genDescriptorFile.close()
        genDescriptorSoup = Soup(genDescriptorXml, "xml")

        