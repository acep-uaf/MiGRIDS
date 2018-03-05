# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 22, 2018
# License: MIT License (see LICENSE file of this package for more information)

import pandas as pd


def getLoadFactor(genAllP, genAllPOutMaxPa):
    """
    Calculates the load factor for all generator power channels provided as input, and a cumulative load factor for the
    sum of all channels.
    :param genAllP: [DataFrame] columns are 'time' and 'genXP' channels where X is the specific generator number
    :param genAllPOutMaxPa: [DataFrame] 'genX' is index, single column 'POutMaxPa' is nameplate power of each gen
    :return: genAllPPu: [DataFrame] same format as genAllP, but with all power values relative to POutMaxP for each
        specific generator and a 'genTotPPu' column with load factor relative to total nameplate capacity.
    """

    # Setup
    genList = genAllPOutMaxPa.index
    genListP = [gen + 'P' for gen in genList]
    genListPu = [gen + 'PPu' for gen in genList]
    gcols = genListPu.copy()
    gcols.insert(0, 'time')
    gcols.append('genTotPPu')
    gcols = pd.Index(gcols[:])
    genAllPPu = pd.DataFrame(genAllP['time'], genAllP.index, gcols)
    genTotPPa = 0

    # Crank through the df to get the values calculated.
    for gen in genList:
        genTotPPa = genTotPPa + int(genAllPOutMaxPa.loc[gen])
        genPPu = genAllP[gen + 'P'] / int(genAllPOutMaxPa.loc[gen])
        genAllPPu[gen + 'PPu'] = genPPu

    # Do the totals.
    genAllPPu['genTotPPu'] = genAllP[genListP].sum(axis=1)/genTotPPa

    return genAllPPu

