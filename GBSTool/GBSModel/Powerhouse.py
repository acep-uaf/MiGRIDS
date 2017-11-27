# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

import Generator()

class Powerhouse:

    # Powerhouse variables
    generators = []
    genIDS = []

    # __init()__ Class constructor. Initiates the setup of the individual generators as per the initial input.
    # TODO: Document inputs
    def __init__(self, genIDS, genP, genQ, genPMaxPa, genQMaxPa, genPAvail, genQAvail):
        self.genIDS = genIDS
        # Populate the list of generators with generator objects
        for idx, genID in enumerate(genIDS):
            self.generators.append(self, Generator(genID, genP(idx), genQ(idx), genPMaxPa(idx), genQMaxPa(idx), genPAvail(idx), genQAvail(idx)))



