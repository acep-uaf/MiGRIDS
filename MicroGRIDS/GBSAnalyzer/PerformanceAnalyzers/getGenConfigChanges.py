# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: March 5, 2018
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np


def getGenConfigChanges(genAllP):
    """
    Calculates the total number of configuration changes for the diesel power house. This assumes that a 'genP' channel
    reading 0 kW means that generator is offline. If the channel reads non-zero and positive the generator is assumed to
    be online.
    Note: if negative values are present, they are deleted [set to 0]

    :param genAllP: [DataFrame] the real power channels for the generator fleet. Function checks if a time channel is
        included and ditches it if needed.
    :return genConfigDeltaTot: [int] total number of generator configuration changes.
    """

    # Check if time stamps were passed along. If so, remove.
    if 'time' in genAllP:
        genAllP = genAllP.drop('time', 1)

    # Just get the booleans for generator running or not (based on non-zero power).
    genBools = np.sign(genAllP)

    # Should there be negative values present (reverse power!) delete those (set to 0).
    genBools[genBools < 0] = 0

    # Get the sum of the booleans for each time stamp
    genBoolsTot = genBools.sum(axis=1)

    # Get the diff of this vector
    genBoolsTotDiff = genBoolsTot.diff()
    # If diff is non-zero, this is a config change.
    genSwitched = np.abs(np.sign(genBoolsTotDiff))

    # Sum is the total number of configuration changes
    genConfigDeltaTot = genSwitched.sum()

    return genConfigDeltaTot

