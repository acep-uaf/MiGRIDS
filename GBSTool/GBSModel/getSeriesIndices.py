# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 7, 2018
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np


def getSeriesIndices(steps, seriesLen):
    if steps == 'all' or steps == ':':
        idx = range(seriesLen)
    elif (type(steps) is list or type(steps) is np.ndarray):
        if len(steps) == 2:
            idx = range(steps[0],steps[1])
        else:
            idx = steps
    elif type(steps) is int:
        idx = range(steps)
    else:
        idx = steps

    return idx