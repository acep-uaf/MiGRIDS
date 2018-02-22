# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 22, 2018
# License: MIT License (see LICENSE file of this package for more information)

from GBSAnalyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve

def getFuelUse(genAllP, fuelCurveDataPoints):
    '''

    :param genAllP: [DataFrame] individual genXP channels and time channel, index is integers numbering samples
    :param fuelCurveDataPoints: [DataFrame] index is generator names, columns are 'fuelCurve_pPu' and
        'fuelCurve_massFlow', 'POutMaxPa'
    :return genAllFuelUsed: [DataFrame] contains individual genX fuel used and time channel, index is integers
    :return fuelStats: [DataFrame] fuel stats for each gen and totals
    '''

    # Step through the data per generator
    genList = fuelCurveDataPoints.index

    for gen in genList:

        pPu = list(map(float, fuelCurveDataPoints['fuelCurve_pPu'].loc[gen].split()))
        pPu[:] = [ x * float(fuelCurveDataPoints['POutMaxPa'].loc[gen])for x in pPu]
        massFlow = list(map(float, fuelCurveDataPoints['fuelCurve_massFlow'].loc[gen].split()))
        fcDataPnts = list(zip(pPu, massFlow))
        fc = GenFuelCurve()
        fc.fuelCurveDataPoints = fcDataPnts
        fc.linearCurveEstimator()
        



