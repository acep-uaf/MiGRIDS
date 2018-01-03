# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import Generator


# import GeneratorDispatch

class Powerhouse:
    '''

    '''
    # ************Powerhouse variables**********************
    # List of generators and their respective IDs
    generators = []
    genIDS = []

    # Generator dispatch object
    genDispatch = None  # TODO: implement GeneratorDispatch()

    # Cumulative operational data
    # Actual loadings
    genP = 0
    genQ = 0
    # Total available gen power without new dispatch
    genPAvail = 0
    genQAvail = 0

    # __init()__ Class constructor. Initiates the setup of the individual generators as per the initial input.
    # Inputs:
    # self - self reference, always required in constructor
    # genIDS - list of generator IDs, which should be integers
    # genP - list of generator real power levels for respective generators listed in genIDS
    # genQ - list of generator reactive power levels for respective generators listed in genIDS
    # genDescriptor - list of generator descriptor XML files for the respective generators listed in genIDS, this should
    #   be a string with a relative path and file name, e.g., /InputData/Components/gen1Descriptor.xml
    def __init__(self, genIDS, genP, genQ, genDescriptor):
        """

        :param genIDS:
        :param genP:
        :param genQ:
        :param genDescriptor:
        """
        self.genIDS = genIDS
        # Populate the list of generators with generator objects
        for idx, genID in enumerate(genIDS):
            # Initialize generators
            self.generators.append(self, Generator(genID, genP[idx], genQ[idx], genDescriptor[idx]))

            # Initial value for genP, genQ, genPAvail and genQAvail can be handled while were in this loop
            self.genP = self.genP + self.generators[idx].genP
            self.genQ = self.genQ + self.generators[idx].genQ
            self.genPAvail = self.genPAvail + self.generators[idx].genPAvail
            self.genQAvail = self.genQAvail + self.generators[idx].genQAvail
