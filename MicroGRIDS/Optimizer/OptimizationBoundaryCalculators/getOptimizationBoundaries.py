# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: March 29, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Interface to run various OptimizationBoundaryCalculator methods. These are dispatched based on user selection.

# Import the functions this serves as interface for
import pandas as pd

from GBSOptimizer.OptimizationBoundaryCalculators.calcSRCMethodBoundaries import calcSRCMethodBoundaries


def getOptimizationBoundaries(boundaryMethod, time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints):
    '''
    Interface to dispatch specific OptimizationBoundaryCalculators as specified in BoundaryMethod. Passes back the
    suggested boundaries for ESS power and energy capacity.

    :param boundaryMethod: sets the calculation method used. Currently, valid inputs are 'variableSRC',
        and 'noBoundaries'. See configuration documentation for more details.
    :type boundaryMethod: str
    :param time: Input time series, is uniform for all power input time series.
    :type time: pd.Series
    :param firmLoadP: Firm load real power time series, i.e., the power demand that always has to be supplied.
    :type firmLoadP: pd.Series
    :param varLoadP: Variable load real power time series, i.e., demand that can be ramped up or down as needed for
        grid balance.
    :type varLoadP: pd.Series
    :param firmGenP: Firm generation real power time series, i.e., generator and energy storage output to the grid.
    :type firmGenP: pd.Series
    :param varGenP: Variable generation real power time series, i.e., all non-load following generation.
    :type varGenP: pd.Series
    :param otherConstraints: any other inputs potentially required by specific OptimizationBoundaryCalculator as a
        list of strings.
    :type otherConstraints: list[str]
    :return:
    :param minESSPPa: Lower real power limit to size ESS with in optimization, kW.
    :type minESSPPa: float
    :param maxESSPPa: Upper real power limit to size ESS with in optimization, kW.
    :type maxESSPPa: float
    :param minESSEPa: Lower energy capacity limit to size ESS with in optimization, kWh.
    :type minESSEPa: float
    :param maxESSEPa: Upper energy capacity limit to size ESS with in optimization, kWh.
    :type maxESSEPa: float
    '''

    # SRCMethod dispatch (currently ony valid method)
    if boundaryMethod == 'variableSRC':
        minESSPPa, maxESSPPa, minESSEPa, maxESSEPa = \
            calcSRCMethodBoundaries(time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints)

    # If 'noBoundaries' is specified the minima are set to zeros and the maxima are set to infinity.
    elif boundaryMethod == 'noBoundaries':
        # TODO test the infinity values are handled properly throughout the code.
        minESSPPa = 0
        minESSEPa = 0
        maxESSPPa = float('Inf')
        maxESSEPa = float('Inf')

    # FUTUREFEATURE: Add other boundary calculators below.
    # elif boundaryMethod == otherBoundary calculator:

    # If the string in boundaryMethod cannot be interpreted, give warning, and default to SRCMethod.
    else:
        raise UserWarning(
            'Unknown method, %s, for optimization boundary calculation specified. Defaulting to variable SRC method.',
            boundaryMethod)
        #minESSPPa, maxESSPPa, minESSEPa, maxESSEPa = calcSRCMethodBoundaries(time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints)

    return minESSPPa, maxESSPPa, minESSEPa, maxESSEPa