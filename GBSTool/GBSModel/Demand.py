# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: November 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# imports
from netCDF4 import Dataset
import numpy as np
from readNCFile import readNCFile

class Demand:

    # Constuctor
    def __init__(self, timeStep, loadRealFiles, loadReactiveFiles = []):
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
        # read the real load in
        self.realLoad = self.loadLoadFiles(loadRealFiles)

        # if loadReactiveFiles is not empty, load reactive files
        if len(loadReactiveFiles) != 0:
            self.reactiveLoad = self.loadLoadFiles(loadReactiveFiles)
        else:
            self.reactiveLoad = np.array([])

    def loadLoadFiles(self,loadFiles, isReal = True):
        # read the real load in
        # check if it is a list or tuple
        if type(loadFiles) is list or type(loadFiles) is tuple:
            for idx, file in enumerate(loadFiles):
                ncFile = readNCFile(file)
                time = ncFile.time
                value = ncFile.value
                scale = ncFile.scale
                offset = ncFile.offset
                timeUnits = ncFile.timeUnits
                valueUnits = ncFile.valueUnits

                # check if any nan values
                if any(np.isnan(time)) or any(np.isnan(value)):
                    raise ValueError(
                        'There are nan values in the load files.')
                # check the units for time
                elif timeUnits.lower() != 's' and timeUnits.lower() != 'sec' and timeUnits.lower() != 'seconds':
                    raise ValueError('The units for time must be s.')
                # check time step to make sure within +- 10% of timeStep input
                # this will have a problem with daylight savings
                #elif min(np.diff(time)) < 0.9 * self.timeStep or max(np.diff(time)) > 1.1 * self.timeStep:
                 #   raise ValueError(
                  #      'The difference in the time stamps is more than the 10% different than the time step defined for '
                  #      'this simulation ({} s). The timestamps should be in epoch format.'.format(self.timeStep))
                elif valueUnits.lower() != 'kw' and isReal:
                    raise ValueError('The units for real load must be kW.')
                elif valueUnits.lower() != 'kvar' and not isReal:
                    raise ValueError('The units for reactive load must be kvar.')

                # if the first file, initiate the real load variable
                if idx == 0:
                    load = np.array(value)*scale + offset
                # otherwise, add on to the previous values
                else:
                    # check length to make sure the same
                    if len(value) != len(load):
                        raise ValueError(
                            'The length of input load files must be equal.')
                    load += np.array(value)*scale + value
            return load

        # if not a list or tuple, this file should represent the total load
        else:
            rootgrp = Dataset(loadFiles, "r", format="NETCDF4")
            time = rootgrp.variables['time']
            value = rootgrp.variables['value']
            scale = rootgrp.variables['value'].Scale
            offset = rootgrp.variables['value'].offset
            units = rootgrp.variables['value'].units
            # check if any nan values
            if any(np.isnan(time)) or any(np.isnan(value)):
                raise ValueError(
                    'There are nan values in the load file.')
            # check time step to make sure within +- 10% of timeStep input
            elif min(np.diff(time)) < 0.9 * self.timeStep or max(np.diff(time)) > 1.1 * self.timeStep:
                raise ValueError(
                    'The difference in the time stamps is more than the 10% different than the time step defined for '
                    'this simulation ({} s). The timestamps should be in epoch format.'.format(self.timeStep))
            elif units.lower() != 'kw' and isReal:
                raise ValueError('The units for real load must be kW.')
            elif units.lower() != 'kvar' and not isReal:
                raise ValueError('The units for reactive load must be kvar.')
            return np.array(value)*scale + offset