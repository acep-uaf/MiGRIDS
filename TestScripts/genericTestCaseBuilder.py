#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:23:08 2018

@author: marcmueller-stoffels

Creates a very generic test case for load and wind speed and available wind power [the latter based on a wtgDescriptor.xml]

Also creates an empty time-series for energy storage.

These time-series can be used as inputs for test model runs under controlled conditions.

CAUTION: The time series are not realistic by any means, but they do allow to look at functionality of dispatch, general
dynamics with the diesel fleet, etc.
"""

import numpy as np
from MicroGRIDS.Analyzer.DataWriters.writeNCFile import writeNCFile
from MicroGRIDS.Model.Components.WindTurbine import WindTurbine

# Turn generation of time-series on or off individually
mkLoad = True
mkWind = True
mkEES = False

# Some presets
offSet = 1514764800 #Unix epoch Jan 1 2017
duration = 365*24*60*60 # One year in seconds
period = 24*60*60 # One day in seconds
timeSteps = np.asarray(list(range(offSet, duration + offSet))) # Series of time stamps

#load0P - Makes generic load series and saves it to load0P.nc
if mkLoad:
    baseLoad = 500

    load0P = baseLoad + 0.5* baseLoad * np.sin(2*np.pi*timeSteps/period) + \
        0.25*baseLoad*np.random.normal(0,0.1,duration)

    writeNCFile(timeSteps, load0P, 1, 0, 'kW', 'load0P.nc')

    #plt.plot(timeSteps[1:], np.diff(load0P)/np.mean(load0P))

# wtg0WS and wtg0WP - makes generic wind speed profile and generates associated wind power profile using power curve
# provided by wtgDescriptor.xml
if mkWind:
    # wtg0P
    meanWindSpeed = 7.5 # m/s
    #weibullShape = 1.75 # Weibull distributions described wind stats well, but using them to regenerate wind speeds in uncorrelated time steps is not going well.
    windPeriod = 15*60*24*365 # Used to add some seasonality to the wind

    # Create multi-phase signal
    wtg0Speed = meanWindSpeed + \
                0.75 * meanWindSpeed * np.sin(2*np.pi * timeSteps/windPeriod) +\
                0.5 * meanWindSpeed * np.sin(2*np.pi * timeSteps/(60*60*24*10)) +\
                0.5 * meanWindSpeed * np.sin(2*np.pi *timeSteps/(60*60*24))
    # Randomize, but keep somewhat correlated
    wtg0Speed = np.random.normal(wtg0Speed,0.1,duration)

    # Get rid of all the values less than zero
    wtg0Speed = np.abs(wtg0Speed)

    #plt.plot(timeSteps[:-1], dwdt)
    #plt.plot(timeSteps, wtg0Speed)
    #plt.show()
    writeNCFile(timeSteps, wtg0Speed, 1, 0, 'm/s', 'wtg0WS.nc')

    # Following line creates wtg0WP.nc
    # NOTE that this assumes that wtg0Descriptor.xml is in the same folder as this script. If this is not the case
    # a path will have to be added.
    wtg0 = WindTurbine(0, '.', 0, 1, 'wtg0Descriptor.xml')

if mkEES:
    # ees0P
    ees0P = 0*timeSteps

    writeNCFile(timeSteps, ees0P, 1, 0, 'kW', 'ees0P.nc')



