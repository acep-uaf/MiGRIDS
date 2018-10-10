# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 22, 2018
# License: MIT License (see LICENSE file of this package for more information)

import numpy as np
import pandas as pd

from Analyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve

def getFuelUse(genAllP, fuelCurveDataPoints, interpolationMethod = 'linear'):
    '''
    Calculates fuel consumption for each generator and time step given.

    FUTUREFEATURE: currently just tosses generator loads greater than POutMaxPa and replaces them with fuel use at 'POutMaxPa'. Better handling of overloads would be good.

    :param genAllP: [DataFrame] individual genXP channels and time channel, index is integers numbering samples
    :param fuelCurveDataPoints: [DataFrame] index is generator names, columns are 'fuelCurve_pPu' and
        'fuelCurve_massFlow', 'POutMaxPa'
    :param interpolationMethod: the interpolation method used for the fuel curve is indicated here. 'linear', 'cubic'
    or 'none' are valid inputs. 'none' indicates no interpolation is needed, the input fuel curve will be used to
    calculate fuel consumption. Default value is 'linear'.
    :return genAllFuelUsed: [DataFrame] contains individual genX fuel used [kg] and time channel, index is integers
    :return fuelStats: [DataFrame] fuel stats for each gen and totals
    '''

    # Step through the data per generator
    genList = fuelCurveDataPoints.index
    gcols = list(genList.values)
    gcols.insert(0, 'time')
    gcols = pd.Index(gcols[:])
    genAllFuelUsed = pd.DataFrame(genAllP['time'], genAllP.index, gcols)

    fuelStats = pd.DataFrame([], genList.append(pd.Index(['Fleet'])), ['total', 'mean', 'std', 'median', 'max'])

    # Get time steps, since the fuel curve is only providing mass flow. Total mass requires multiplication by time.
    dt = genAllP['time'].diff()
    fleetSum = np.zeros(np.shape(dt))

    for gen in genList:

        pPu = list(map(float, fuelCurveDataPoints['fuelCurve_pPu'].loc[gen].split()))
        pPu[:] = [ x * float(fuelCurveDataPoints['POutMaxPa'].loc[gen])for x in pPu]
        massFlow = list(map(float, fuelCurveDataPoints['fuelCurve_massFlow'].loc[gen].split()))
        fcDataPnts = list(zip(pPu, massFlow))
        fc = GenFuelCurve()
        fc.genOverloadPMax = int(float(fuelCurveDataPoints['POutMaxPa'].loc[gen])) #double type cast is necessary to handle string conversion of strings with decimals properly.
        fc.fuelCurveDataPoints = fcDataPnts
        fc.linearCurveEstimator()

        # Get the 'indices' (power levels) for which to retrieve fuel data for
        retrieveIdx = genAllP[gen + 'P'].values.astype(int)

        # If there's bad data [exceeding index in fc.fuelCurve] it needs to be tossed.
        retrieveIdx[retrieveIdx > len(fc.fuelCurve)-1] = len(fc.fuelCurve)-1

        # PERFORMANCE: the following line costs a ton of time. Consider better options. Note that itemgetter did not work.
        genFuel = [fc.fuelCurve[ridx][1] for ridx in retrieveIdx]
        genFuel = genFuel * dt
        fleetSum = fleetSum + genFuel
        genAllFuelUsed[gen] = genFuel
        fuelStats['total'].loc[gen] = genFuel.sum()
        fuelStats['mean'].loc[gen] = genFuel.mean()
        fuelStats['std'].loc[gen] = genFuel.std()
        fuelStats['median'].loc[gen] = genFuel.median()
        fuelStats['max'].loc[gen] = genFuel.max()

    fuelStats['total'].loc['Fleet'] = fleetSum.sum()
    fuelStats['mean'].loc['Fleet'] = fleetSum.mean()
    fuelStats['std'].loc['Fleet'] = fleetSum.std()
    #fuelStats['median'].loc['Fleet'] = fleetSum.median() # not available as ndarray.median()
    fuelStats['max'].loc['Fleet'] = fleetSum.max()

    return genAllFuelUsed, fuelStats



