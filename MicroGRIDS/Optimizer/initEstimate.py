# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Develops initial sizing estimate based on a collection of approaches.

class initEstimate:
    '''
    initEstimate class contains a collection of methods to ascertain boundary conditions for the optimization of the GBS
    sizing.
    '''

    def __init__(self, time, loadP, firmGenP, varGenP):
        '''
        Constructor initializes time-series required to calculate initial rough sizing estimates.

        :param time: [Series] time vector
        :param loadP: [Series]
        :param firmGenP:
        :param varGenP:
        '''

