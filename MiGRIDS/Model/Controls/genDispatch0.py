
# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: October 1, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

class genDispatch:
    def runDispatch(self,ph, newGenP, newGenQ = 0):
        """
        dispatch the power setpoints for each diesel generator.
        :param ph: a powerhouse object
        :param newGenP: the new total real power requested
        :param newGenQ: the new totla reactive power requested (this is not implemented yet).
        """
        # make genPAvail and genQAvail have been updated
        # check if no diesel generators online. still assign power, this will be flagged as a power outage
        # Helper sum
        sumGenPAvail = sum(ph.genPAvail)
        if sumGenPAvail == 0:
            for idx in range(len(ph.genIDS)):
                ph.generators[idx].genP = newGenP / len(ph.genIDS)
                ph.generators[idx].genQ = newGenQ / len(ph.genIDS)
                # update the local variable that keeps track of generator power
                ph.genP[idx] = ph.generators[idx].genP
                ph.genQ[idx] = ph.generators[idx].genQ
        else:
            loadingP = newGenP / max(sumGenPAvail,
                                     1)  # this is the PU loading of each generator. max with 1 for 0 capacity instance
            loadingQ = newGenQ / max(sum(ph.genQAvail), 1)  # this is the PU loading of each generator
            # cycle through each gen and update with new P and Q
            for idx in range(len(ph.genIDS)):
                ph.generators[idx].genP = loadingP * ph.generators[idx].genPAvail
                ph.generators[idx].genQ = loadingQ * ph.generators[idx].genQAvail
                # update the local variable that keeps track of generator power
                ph.genP[idx] = ph.generators[idx].genP
                ph.genQ[idx] = ph.generators[idx].genQ
