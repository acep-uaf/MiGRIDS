# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: March 29, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Uses SRC considerations to estimate optimization boundaries for power and energy of an ESS
import pandas as pd

def calcSRCMethodBoundaries(time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints):
    '''
    The SRC Method searches the GBS size that always is able to meet the dynamic SRC requirement and can support this
    requirement for a minimum of `minDuration' seconds. It uses the case of meeting SRC requirements in `minPercent` as
    the minimum percentile for which the GBS has to provide SRC and `maxPercentile` as the maximum percentile for which
    the GBS has to meet SRC requirements, multiplied by a margin `maxMargin`. `minDynSRC` determines the minimum fraction
    of firm demand that has to be held as SRC.

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
    :param otherConstraints: [minDynSRC, minDuration, minPercent, maxPercent, maxMargin]
        minDynSRC is a fraction
        minDuration is a time in seconds
        minPercent is a reference to a percentile as a fraction
        maxPercent is a reference to a percentile as a fraction
        maxMargin is a reference to the margin put on the maximum power calculated as a fraction
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

    # Handle conversion of inputs contained in `otherConstraints` to usable numbers
    minDynSRC = float(otherConstraints[0])
    minDuration = int(otherConstraints[1])
    minPercent = float(otherConstraints[2])
    maxPercent = float(otherConstraints[3])
    maxMargin = float(otherConstraints[4])


    # Calculate SRC time series -> SRC always has to be either the minDynSRC fraction of current demand, or the
    # current contribution of varGenP to meeting firmLoadP.
    # Get the contribution of varGenP to firmLoadP. By definition, this must be all firmLoadP not met by firmGenP
    varGenPContrib = firmLoadP - firmGenP
    # Get min SRC as a percentage of each load data point
    SRCPMin = minDynSRC * firmGenP

    # Get actual SRC parameter for each time step
    SRCPPa = SRCPMin.copy()
    SRCPPa[varGenPContrib > SRCPMin] = varGenPContrib[varGenPContrib > SRCPMin]

    # Get the power level boundaries
    minESSPPa = SRCPPa.quantile(minPercent)
    maxESSPPa = SRCPPa.quantile(maxPercent) * maxMargin

    # Get the min energy capacity at the min and max power level
    minESSEPa = minESSPPa * minDuration / 3600 # Conversion to kWh
    maxESSEPa = maxESSPPa * minDuration / 3600

    return minESSPPa, maxESSPPa, minESSEPa, maxESSEPa