# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# INITIAL ESS ESTIMATOR contains routines to preliminarily estimate the power and energy size range envelope in which to
# search for the most optimal solutions. For this, the physical limitations (maximum ramping capability, minimum start
# time) of the diesel generator fleet are used. The approach is quite brute force, but should yield a reduction in search
# range nonetheless.
#
# Functions:
# GETTOTALGROSSLOAD
# LOADDATA

from bs4 import BeautifulSoup as bs
import datetime
import netCDF4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from GBSController.GBSExceptions.TimeStampVectorError import TimeStampVectorError
import itertools


def getTotalGrossLoad(projectPath, projectName):
    """
    Calculates the total gross load based on available input time series. It is assumed that these input time series are
    in the prescribed netCDF format. Total gross load is defined as the real power sum of all generation assets (sources).

    :param projectPath: [string] path to the projects 'projectSetup.xml'
    :return time: [Series] time stamps for the total load time series
    :return loadP: [Series] time series of the total load.
    :return cumPMaxOut: [float] cumulative nameplate generation capacity
    :return msg: [list of String] status messages for logging or feedback
    """

    # Setup load and time
    loadP = pd.Series()
    genP = pd.Series()
    wtgP = pd.Series()
    otherP = pd.Series()
    cumPOutMaxPa = 0
    # Setup status message bin
    msg = []

    # Construct path to 'projectSetup'
    projectSetup = projectPath + 'InputData/Setup/' + projectName + 'Setup.xml'
    msg.append('Project path: ' + projectSetup)

    # Search all 'source' assets
    projectSetupFile = open(projectSetup, "r")
    projectSetupXML = projectSetupFile.read()
    projectSetupFile.close()
    projectSoup = bs(projectSetupXML, "xml")
    components = projectSoup.componentNames.get("value").split()
    msg.append('Project components found: ' + ' '.join(components))

    # Iterate through components and check if they are a source.
    for component in components:

        componentString = component
        componentPath = projectPath + 'InputData/Components/' + componentString + 'Descriptor.xml'
        msg.append('Loading: ' + componentPath)
        componentFile = open(componentPath, 'r')
        componentFileXML = componentFile.read()
        componentFile.close()
        componentSoup = bs(componentFileXML, "xml")

        # Now we need to check if the component selected is a source
        if componentSoup.type.get('value') == 'source':
            # Construct path to the input data file
            dataFilePath = projectPath + 'InputData/TimeSeriesData/ProcessedData/' + componentString +'P.nc'
            msg.append('Loading: ' + dataFilePath)
            msg.append('Adding ' + componentString + 'P to gross load sum.')
            tempLoadP, tempTime, tempTS, tempSD, tempED = loadData(dataFilePath)
            # Note the start and end dates for comparison
            refSD = tempSD
            refED = tempED
            time = tempTime
            ts = tempTS

            # Sum up the total generation nameplate capacity
            cumPOutMaxPa = cumPOutMaxPa + int(componentSoup.POutMaxPa.get("value"))

            # Handle first entry
            if loadP.empty:
                loadP = pd.Series(tempLoadP)
            elif tempSD == refSD and tempED == refED and loadP.shape == tempLoadP.shape:
                loadP = loadP.add(tempLoadP)
            else:
                msg.append('Terminated due to data consistency issue in ' + componentString + 'P.nc')
                raise TimeStampVectorError([tempSD, tempED], "Consistency issue with time series inputs.")

            if componentSoup.component.get('name')[:3] == 'gen':
                # Handle first entry
                if genP.empty:
                    genP = pd.Series(tempLoadP)
                else:
                    genP = genP.add(tempLoadP)
            elif componentSoup.component.get('name')[:3] == 'wtg':
                # Handle first entry
                if wtgP.empty:
                    wtgP = pd.Series(tempLoadP)
                else:
                    wtgP = wtgP.add(tempLoadP)
            else:
                # Handle first entry
                if otherP.empty:
                    otherP = pd.Series(tempLoadP)
                else:
                    otherP = otherP.add(tempLoadP)


    return time, ts, loadP, genP, wtgP, otherP, refSD, refED, cumPOutMaxPa, msg


def loadData(filePath):
    """
    Helper function to load a netCDF data file. Returns the time and value arrays separately and does a few convenience
    things for the time vector if wanted/needed.
    :param filePath:
    :return value: [Series] the series of values from the netCDF file
    :return time: [Series] the series of time stamps in UNIX epoch from the netCDF file
    :return timeStamps: [datetime array] timestamps in datetime format (useful for plotting and such)
    :return startDate: [datetime array] start date and time, i.e., value for the first entry in time
    :return endDate: [datetime array] end date and time, i.e., value for the last entry in time
    """
    nc = netCDF4.Dataset(filePath)
    value = pd.Series(nc.variables['value'][:])
    time = pd.Series(nc.variables['time'][:])

    # Get time stamps for convenience.
    timeStamps = [datetime.datetime.fromtimestamp(ts) for ts in time]

    startDate = datetime.datetime.fromtimestamp(time[0])
    endDate = datetime.datetime.fromtimestamp(time.iloc[-1])

    return value, time, timeStamps, startDate, endDate


def checkTSData(time, loadP, cumPOutMaxPa, timeStepCutOff = 5, maxTimeStepAcceptedFactor = 1.1):
    """
    checkData does a cursory check of the time step sizes, and flags artifacts that clear are due to outages (data or
    physical) so that they are not part of any future ramp rate considerations. Note that 'normal' time step size is
    'guessed' using the median of the differences in time steps. This is based on the assumption, that most time steps
    are of the median size, while mean values could be skewed by a few long outages.
    :param time: [Series] time vector, time is assumed to be in unix epochs
    :param loadP: [Series] load vector, load is assumed to be in kW
    :param cumPOutMaxPa: total sum of generating nameplate capacity, loads above this value should be tossed.
    :param timeStepCutOff: [float] maximum time step size where ramp rate assessment still is recommended
    :param maxTimeStepAcceptedFactor: [float] factor to calculate maximum time step size not flagged as out of bounds
        for subsequent assessments as a function of the median time step size.
    :return status: [integer] status flag, TRUE if ramp-rate assessment ok (avg. deltaT <= timeStepCutOff), FALSE else.
    :return ignoreIdx: [Series] list of indices with black listed ramp rates due to outages
    :return msg: [List of strings] status messages for the log file
    """
    status = False
    ignoreIdx = np.empty(0, dtype=int)
    msg = []

    # *** Check delta-T and set status accordingly ***
    # Get differences in time stamps and run simple stats
    dt = np.diff(time)
    medianDt = np.nanmedian(dt)
    meanDt = np.nanmean(dt)

    # Record for log or messaging
    msg.append('Mean difference between time stamps: ' + str(meanDt) + ' s')
    msg.append('Median difference between time stamps : ' + str(medianDt) + ' s')

    # Check step size and set status accordingly
    if medianDt <= timeStepCutOff  and medianDt > 0:
        status = True
        msg.append('Time steps sufficiently small, ramp rate assessment recommended.')
    elif medianDt > timeStepCutOff:
        status = False
        msg.append('Time steps are too large, ramp rate assessment not recommended.')
    else:
        status = False
        raise TimeStampVectorError(medianDt, 'Time stamp issue, causality not preserved: median dt < 0.')

    # *** Blacklist large differences between time steps ***
    for idx, dtVal in np.ndenumerate(dt):
        if dtVal > maxTimeStepAcceptedFactor*medianDt:
            ignoreIdx = np.append(ignoreIdx,idx)
            #print('Index added to igIdx: ' + str(idx))

    # *** Search for 'drops to zero' and 'rises from zero' - blacklist in ignoreIdx as outages. Also add all 0 kW
    # entries to the ignoreIdx ***

    # Previous value in time series, random value initially
    prevVal = 100

    #Step through the loadP vector and search for rises from and drops to 0 kW
    for i, val in np.ndenumerate(loadP):
        if val == 0 and prevVal != 0:
            ignoreIdx = np.append(ignoreIdx, i)
            msg.append('Drop from ' + str(prevVal) + ' kW to 0 kW detected. Index: ' + str(i))
        elif prevVal == 0 and val != 0:
            msg.append('Rise from 0 kW to ' + str(val) + ' kW detected. Index: ' + str(i))
            ignoreIdx = np.append(ignoreIdx, i)
        elif val == 0:
            ignoreIdx = np.append(ignoreIdx, i)
            msg.append('0 kW value found at index: ' + str(i))
        prevVal = val

    # *** Search for excessively high loads ***
    ignoreIdx = np.append(ignoreIdx, loadP[loadP > cumPOutMaxPa].index.values)

    # The ignoreIdx needs some cleaning up: remove duplicates, and sort ascending
    ignoreIdx = np.unique(ignoreIdx)
    ignoreIdx.sort(0)

    return status, ignoreIdx, msg

def dieselFleetCheck(projectPath, projectName):
    '''
    Loads the key parameters for the diesel fleet. This is used for a very preliminary sizing based on generator
    nameplate differences. The available capacity steps are calculated for every possible powerhouse configuration
    (sorted by actual available capacity in each configuration).
    :param projectPath:
    :param projectName:
    :return dieselFleet: [DataFrame] nameplate capacities of available diesels
    :return configDeltaP: [Series] the power gaps between all possible diesel powerhouse configurations
    '''
    dieselFleet = pd.DataFrame([])
    configDeltaP = []

    # Load pertinent information from project xml files
    # Setup status message bin
    msg = []

    # Construct path to 'projectSetup'
    projectSetup = projectPath + 'InputData/Setup/' + projectName + 'Setup.xml'
    msg.append('Project path: ' + projectSetup)

    # Search all 'gen' assets
    projectSetupFile = open(projectSetup, "r")
    projectSetupXML = projectSetupFile.read()
    projectSetupFile.close()
    projectSoup = bs(projectSetupXML, "xml")
    components = projectSoup.componentNames.get("value").split()
    msg.append('Project components found: ' + ' '.join(components))

    index = list()
    genPAvail = list()
    componentSoupBowl = list()
    # Iterate through components and check if they are a generator.
    for component in components:

        componentString = component
        componentPath = projectPath + 'InputData/Components/' + componentString + 'Descriptor.xml'
        msg.append('Loading: ' + componentPath)
        componentFile = open(componentPath, 'r')
        componentFileXML = componentFile.read()
        componentFile.close()
        componentSoup = bs(componentFileXML, "xml")

        # Now we need to check if the component selected is a gen and record that gen to the index for our dataframe
        if componentSoup.component.get('name')[0:3] == 'gen':
            index.append(componentSoup.component.get('name'))
            componentSoupBowl.append(componentSoup)

    dieselFleet = pd.DataFrame([], index)

    # Step through each generator descriptor an construct the DF from it.

    # First we'll construct the column names - note that we only want columns with tag names that carry actual values.
    # Hence, if a tag merely is a container of further tags, it is pitched.
    for child in componentSoupBowl[0].component.find_all():

        # If the child has further children tags, add these to the column name
        if child.parent != componentSoupBowl[0].component:
            colName = child.parent.name + '_' + child.name
            #if child.parent.name in cols:
            #    cols.remove(child.parent.name)
        else:
            colName = child.name

        # Now retrieve the values for this column
        val = []
        if child.get('value') != None:
            val.append(child.get('value'))
            for j in range(1,len(componentSoupBowl)):
                val.append(componentSoupBowl[j].component.find(child.name).get('value'))
            dieselFleet[colName] = val

    # Step through all fleet combinations get their respective combined nameplates
    POutMaxPaSeries = pd.Series([0], ['none'])
    fleetSize = len(index)
    # Step trough the binomials (n = fleetSize), ignore k = 0
    for k in range(1, fleetSize + 1):
            for combination in itertools.combinations(dieselFleet.index, k):
                POutMaxPaSum = 0
                idx = ''
                for s in range(0, len(combination)):
                    POutMaxPaSum = POutMaxPaSum + int(dieselFleet['POutMaxPa'][combination[s]])
                    idx = idx + combination[s] + '_'

                #print(POutMaxPaSeries)
                POutMaxPaSeries = POutMaxPaSeries.append(pd.Series([POutMaxPaSum], [idx[:-1]]))

    # Sort by size to get right diffs
    POutMaxPaSeries.sort_values(inplace=True)
    # Get the step sizes
    configDeltaP = POutMaxPaSeries.diff()

    return dieselFleet, configDeltaP

def getMaxFilteredRampRate(time, loadP, rampTime, ignoreIndex):
    """
    Searches for maximum ramp rate in a given time window (ramp time, should be normal time to dispatch a generator. If
    an 'ignoreIndex' is part of the ramping interval considered the entire interval is discarded.
    :param loadP: [ndarray of int32] load time series
    :param rampTime: [int]  ramp time interval length to consider [Units: seconds]
    :param ignoreIndex: [ndarray of int32] container of blacklisted indices.
    :return maxRampRate:
    :return rampRateDistr:
    """

    # Setup some generic outputs
    maxRampRate = 0
    rampRateDistr = 0

    # Remove bad values from loadP
    loadP[ignoreIndex] = np.nan

    # Get the discrete derivative of loadP
    rampRate = loadP.diff().divide(time.diff())

    # Get the worst case in every rampTime window
    wdwLoadChange = rampRate.rolling(rampTime).mean()

    print('Max mean load ramp: ' + str(wdwLoadChange.max()))
    print('99.9th percentile: ' + str(wdwLoadChange.quantile(.999)))
    print('95th percentile: ' + str(wdwLoadChange.quantile(.95)))

    return rampRate, wdwLoadChange

# **** EXECUTION ***

time, timeStamps, loadP, genP, wtgP, otherP, startDate, endDate, cumPMaxOut, msgGTGL = getTotalGrossLoad('../../GBSProjects/Chevak/','Chevak')

# Setup a dummy 1-s time vector
timeF = time.copy()
timeF = pd.Series(range(0, len(time)) + time[0], time.index)

# Check loadP data
print('++++++++++++ TOTAL DEMAND ASSESSMENT +++++++++++')
stat, igIdx, msgCTSD =checkTSData(time, loadP, cumPMaxOut, 5, 1.1)
print(msgCTSD[0:2])

# Get rampRates for loadP
rr, wdwLoadChng = getMaxFilteredRampRate(timeF.copy(), loadP.copy(), 30, igIdx)

# Check genP data
print('++++++++++++ GENERATOR DEMAND ASSESSMENT +++++++++++')
dfl, cdp = dieselFleetCheck('../../GBSProjects/Chevak/','Chevak')
statGen, igIdxGen, msgCTSD =checkTSData(time, genP, dfl['POutMaxPa'].astype('int').sum(), 5, 1.1)

# Get rampRates for loadP
rrGen, wdwLoadChngGen = getMaxFilteredRampRate(timeF.copy(), genP.copy(), 30, igIdx)

# Check wtgP data
print('++++++++++++ WIND DEMAND ASSESSMENT +++++++++++')
statWtg, igIdxWtg, msgCTSD =checkTSData(time, wtgP, 440, 5, 1.1)

# Get rampRates for loadP
rrWtg, wdwLoadChngWtg = getMaxFilteredRampRate(timeF.copy(), wtgP.copy(), 30, igIdx)

#plt.figure(figsize=(8, 5.5))
# Matplotlib formated timestamps for plotting routines.
#mpTimeStamps = md.date2num(timeStamps)
#plt.plot(time[1:], 200*np.diff(loadP)/np.nanmedian(np.diff(time)))
#plt.plot(timeF, rr)
#plt.plot(timeF, wdwLoadChng)
#plt.plot(timeF, rr)
#wdwLoadChng.hist(bins=100, normed=1, cumulative=True)

#plt.show()
