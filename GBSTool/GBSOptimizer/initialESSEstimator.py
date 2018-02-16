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
import matplotlib.pyplot as plt
import matplotlib.dates as md
from TimeStampVectorError import TimeStampVectorError


def getTotalGrossLoad(projectPath, projectName):
    """
    Calculates the total gross load based on available input time series. It is assumed that these input time series are
    in the prescribed netCDF format. Total gross load is defined as the real power sum of all generation assets (sources).

    :param projectPath: [string] path to the projects 'projectSetup.xml'
    :return time: [Series] time stamps for the total load time series
    :return loadP: [Series] time series of the total load.
    """

    # Setup load and time
    loadP = []
    time = []

    # Construct path to 'projectSetup'
    projectSetup = projectPath + 'InputData/Setup/' + projectName + 'Setup.xml'
    print('Project path: ' + projectSetup)

    # Search all 'source' assets
    projectSetupFile = open(projectSetup, "r")
    projectSetupXML = projectSetupFile.read()
    projectSetupFile.close()
    projectSoup = bs(projectSetupXML, "xml")
    components = projectSoup.componentNames.get("value").split()
    print('Project components found: ' + ' '.join(components))

    # Iterate through components and check if they are a source.
    for component in components:

        componentString = component
        componentPath = projectPath + 'InputData/Components/' + componentString + 'Descriptor.xml'
        print('Loading: ' + componentPath)
        componentFile = open(componentPath, 'r')
        componentFileXML = componentFile.read()
        componentFile.close()
        componentSoup = bs(componentFileXML, "xml")

        # Now we need to check if the component selected is a source
        if componentSoup.type.get('value') == 'source':
            # Construct path to the input data file
            dataFilePath = projectPath + 'InputData/TimeSeriesData/ProcessedData/' + componentString +'P.nc'
            print('Loading: ' + dataFilePath)
            print('Adding ' + componentString + 'P to gross load sum.')
            tempLoadP, tempTime, tempTS, tempSD, tempED = loadData(dataFilePath)
            # Note the start and end dates for comparison
            refSD = tempSD
            refED = tempED
            time = tempTime
            ts = tempTS

            # Handle first entry
            if loadP == []:
                loadP = tempLoadP
            elif tempSD == refSD and tempED == refED and loadP.shape == tempLoadP.shape:
                loadP = loadP + tempLoadP
            else:
                print('Consistency issue with time series inputs.')

    return time, ts, loadP, refSD, refED


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
    value = np.asarray(nc.variables['value'])
    time = np.asarray(nc.variables['time'])

    # Get time stamps for convenience.
    timeStamps = [datetime.datetime.fromtimestamp(ts) for ts in time]

    startDate = datetime.datetime.fromtimestamp(time[0])
    endDate = datetime.datetime.fromtimestamp(time[-1])

    return value, time, timeStamps, startDate, endDate

def checkTSData(time, loadP, timeStepCutOff = 5, maxTimeStepAcceptedFactor = 1.1, maxRampFactor = 1.5):
    """
    checkData does a cursory check of the time step sizes, and flags artifacts that clear are due to outages (data or
    physical) so that they are not part of any future ramp rate considerations. Note that 'normal' time step size is
    'guessed' using the median of the differences in time steps. This is based on the assumption, that most time steps
    are of the median size, while mean values could be skewed by a few long outages.
    :param time: [Series] time vector, time is assumed to be in unix epochs
    :param loadP: [Series] load vector, load is assumed to be in kW
    :param timeStepCutOff: [float] maximum time step size where ramp rate assessment still is recommended
    :param maxTimeStepAcceptedFactor: [float] factor to calculate maximum time step size not flagged as out of bounds
        for subsequent assessments as a function of the median time step size.
    :param maxRampFactor: maximum ramping not considered a data artefact as function of median, non-zero load.
    :return status: [integer] status flag, TRUE if ramp-rate assessment ok (avg. deltaT <= timeStepCutOff), FALSE else.
    :return ignoreIdx: [Series] list of indices with black listed ramp rates due to outages
    :return msg: [List of strings] status messages for the log file
    """
    status = False
    ignoreIdx = []
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
            ignoreIdx.append(idx)

    # *** Search for 'drops to zero' and 'rises from zero' - blacklist in ignoreIdx as outages. Also add all 0 kW
    # entries to the ignoreIdx ***

    # Previous value in time series, random value initially
    prevVal = 100

    #Step through the loadP vector and search for rises from and drops to 0 kW
    for i, val in np.ndenumerate(loadP):
        if val == 0 and prevVal != 0:
            ignoreIdx.append(i)
            msg.append('Drop from ' + str(prevVal) + ' kW to 0 kW detected. Index: ' + str(i))
        elif prevVal == 0 and val != 0:
            msg.append('Rise from 0 kW to ' + str(val) + ' kW detected. Index: ' + str(i))
            ignoreIdx.append(i)
        elif val == 0:
            ignoreIdx.append(i)
            msg.append('0 kW value found at index: ' + str(i))
        prevVal = val

    # *** Search for excessive ramp rates that are likely to be a data artifact ***
    medianLoadP = np.nanmedian(loadP)
    print(medianLoadP/medianDt)
    loadDP = np.diff(loadP)

    for j, valDP in np.ndenumerate(loadDP):
        if np.abs(valDP/medianDt) >= maxRampFactor*medianLoadP/medianDt:
            ignoreIdx.append(j)
            msg.append('Excessive ramping found : ' + str(valDP/medianDt) + ' kW/s at index ' + str(j))


    # The ignoreIdx needs some cleaning up: remove duplicates, and sort ascending
    ignoreIdx = np.unique(ignoreIdx)
    ignoreIdx.sort(0)

    return status, ignoreIdx, msg

def loadDieselFleet(projectPath, ProjectName):
    '''
    Loads the key parameters for the diesel fleet. This is used for a very preliminary sizing based on generator
    nameplate differences.
    :param projectPath:
    :param ProjectName:
    :return dieselNameplates: [list] nameplate capacities of available diesels
    '''

    # TODO: load and sort the diesel data [consider what other data from the xml files might be needed.]

    return dieselNameplates

def getMaxFilteredRampRate(loadP, rampTime, ignoreIndex):
    """
    Searches for maximum ramp rate in a given time window (ramp time, should be normal time to dispatch a generator. If
    an 'ignoreIndex' is part of the ramping interval considered the entire interval is discarded.
    :param loadP: [ndarray of int32] load time series
    :param rampTime: [int]  ramp time interval length to consider [Units: seconds]
    :param ignoreIndex: [ndarray of int32] container of blacklisted indices.
    :return maxRampRate:
    :return rampRateDistr:
    """
    maxRampRate = 0
    rampRateDistr = 0

    # TODO: implement this [find 1-s data for bootstrap prototyping]

    return maxRampRate, rampRateDistr

# **** EXECUTION ***

time, timeStamps, loadP, startDate, endDate = getTotalGrossLoad('../../GBSProjects/Chevak/','Chevak')

stat, igIdx, msg =checkTSData(time, loadP, 5, 1.5)

print(len(time), type(loadP[1]), len(igIdx))
timeF = time.copy()
#timeF[igIdx] = -10
loadPF = loadP.copy()
loadPF[igIdx] = -10

plt.figure(figsize=(8, 5.5))
# Matplotlib formated timestamps for plotting routines.
mpTimeStamps = md.date2num(timeStamps)
#plt.plot(time[1:], 200*np.diff(loadP)/np.nanmedian(np.diff(time)))

plt.plot(time, loadPF)
plt.plot(time[igIdx], loadPF[igIdx],'.')

plt.show()
