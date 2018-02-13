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

def checkTSData(time, loadP):
    """
    checkData does a cursory check of the time step sizes, and flags artifacts that clear are due to outages (data or
    physical) so that they are not part of any future ramp rate considerations.
    :param time: [Series] time vector, time is assumed to be in unix epochs
    :param loadP: [Series] load vector, load is assumed to be in kW
    :return status: [integer] status flag, 1 if ramp-rate assessment ok (avg. deltaT < 5 s), 0 else.
    :return ignoreIdx: [Series] list of indices with black listed ramp rates due to outages
    """
    status = 0
    ignoreIdx = []

    # TODO: check delta-T and set status accordingly
    # TODO: search for 'drops to zero' and 'rises from zero' - blacklist in ignoreIdx as outages.

    return status, ignoreIdx

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



time, timeStamps, loadP, startDate, endDate = getTotalGrossLoad('../../GBSProjects/Chevak/','Chevak')

print(len(time), type(loadP))

plt.figure(figsize=(8, 5.5))
# Matplotlib formated timestamps for plotting routines.
mpTimeStamps = md.date2num(timeStamps)
plt.plot(time[1:], np.diff(time))
plt.show()
