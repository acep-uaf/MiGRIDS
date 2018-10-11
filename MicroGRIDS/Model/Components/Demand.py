# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)


import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from bs4 import BeautifulSoup as Soup
from Analyzer.DataRetrievers.readNCFile import readNCFile
# imports
from Model.Operational.getSeriesIndices import getSeriesIndices


class Demand:

    # Constuctor
    def __init__(self, timeStep, loadRealFiles, loadDescriptor, loadReactiveFiles = [], runTimeSteps = 'all', ):
        """
        Constructors used for initialization of load profiles
        :param timeStep: the time step in seconds that the simulation will be run at
        :param loadRealFiles: net cdf files of the real load. This needs to have variables 'time' and 'value'. 'time needs
        to be in epoch time. This can be one file or a list of files that
        :param loadReactiveFiles: net cdf file of the reactive load. This needs to have variables 'time' and 'value'.
        'time needs to be in epoch time. This can be left empty.
        """
        # the timestep the simulation is run at.
        self.timeStep = timeStep
        # steps to run
        self.runTimeSteps = runTimeSteps
        # read the real load in
        self.realTime, self.realLoad = self.loadLoadFiles(loadRealFiles)
        # Get 10-min trend for getMinSrc0.py
        self.realLoad10minTrend = np.asarray(pd.Series(self.realLoad).rolling(int(600/self.timeStep), min_periods=1).mean())
        # Get 1-hr trend for predictLoad0.py
        self.realLoad1hrTrend = np.asarray(
            pd.Series(self.realLoad).rolling(int(3600 / self.timeStep), min_periods=1).mean())
        # if loadReactiveFiles is not empty, load reactive files
        if len(loadReactiveFiles) != 0:
            self. reactiveTime, self.reactiveLoad = self.loadLoadFiles(loadReactiveFiles)
        else:
            self.reactiveTime = np.array([])
            self.reactiveLoad = np.array([])

        self.loadDescriptorParser(loadDescriptor[0]) # currently can only handle one load

    def loadDescriptorParser(self, loadDescriptor):
        # read xml file
        loadDescriptorFile = open(loadDescriptor, "r")
        loadDescriptorXml = loadDescriptorFile.read()
        loadDescriptorFile.close()
        loadSoup = Soup(loadDescriptorXml, "xml")

        # Dig through the tree for the required data
        self.loadName = loadSoup.component.get('name')
        self.loadPMax = float(loadSoup.PInMaxPa.get('value'))  # maximum load
        self.minSRC = float(loadSoup.minSRC.get('value'))  # min required SRC as fraction of load

    def loadLoadFiles(self,loadFiles):
        # read the real load in
        # check if it is a list or tuple
        if type(loadFiles) is list or type(loadFiles) is tuple:
            for idx, file in enumerate(loadFiles):
                ncFile = readNCFile(file)
                time, load0 = self.checkNCFile(ncFile)

                # if the first file, initiate the real load variable
                if idx == 0:
                    load = load0
                # otherwise, add on to the previous values
                else:
                    # check length to make sure the same
                    if len(load0) != len(load):
                        raise ValueError(
                            'The length of input load files must be equal.')
                    load += load0
        # if not a list or tuple, this file should represent the total load
        else:
            ncFile = readNCFile(loadFiles)
            time, load = self.checkNCFile(ncFile)
        # interpolate wind power according to the desired timestep
        f = interp1d(time, load)
        #TODO: cannot assume the timestep is 1 sec
        num = int(len(time) / self.timeStep)
        timeNew = np.linspace(time[0], time[-1], num)
        loadNew = f(timeNew)
        # get the indices of the timesteps to simulate
        indRun = getSeriesIndices(self.runTimeSteps, len(loadNew))
        return timeNew[indRun], loadNew[indRun]

    def checkNCFile(self,ncFile, isReal = True):
        time = ncFile.time
        value = ncFile.value
        scale = ncFile.scale
        offset = ncFile.offset
        timeUnits = ncFile.timeUnits
        valueUnits = ncFile.valueUnits

        # check if any nan values
        if np.isnan(time).any() or np.isnan(value).any():
            raise ValueError(
                'There are nan values in the load files.')
        # check the units for time
        elif timeUnits.lower() != 's' and timeUnits.lower() != 'sec' and timeUnits.lower() != 'seconds':
            raise ValueError('The units for time must be s.')
            # check time step to make sure within +- 10% of timeStep input
            # this will have a problem with daylight savings
            # elif min(np.diff(time)) < 0.9 * self.timeStep or max(np.diff(time)) > 1.1 * self.timeStep:
            #   raise ValueError(
            #      'The difference in the time stamps is more than the 10% different than the time step defined for '
            #      'this simulation ({} s). The timestamps should be in epoch format.'.format(self.timeStep))
        elif valueUnits.lower() != 'kw' and isReal:
            raise ValueError('The units for real load must be kW.')
        elif valueUnits.lower() != 'kvar' and not isReal:
            raise ValueError('The units for reactive load must be kvar.')
        return time, np.array(value)*scale + offset
