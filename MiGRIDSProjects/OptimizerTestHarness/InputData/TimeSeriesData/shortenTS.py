# Shortens the Chevak netCDF files for test runs.

from os import listdir

import numpy as np
from os.path import isfile, join

from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile
from GBSAnalyzer.DataWriters.writeNCFile import writeNCFile

ncFiles = [f for f in listdir('.') if isfile(join('.', f))]

print(ncFiles)

''' We're done with this
for ncFile in ncFiles:
    if ncFile[-2:] == 'nc':
        nc = readNCFile(ncFile)
        ncTime = nc.time
        ncVal = nc.value
        ncScale = nc.scale
        ncOffSet = nc.offset
        ncTimeUnits = nc.timeUnits
        ncValUnits = nc.valueUnits

        strIdx = 1000000
        dayIdx = 84600
        remove(ncFile)
        ncWrt = writeNCFile(ncTime[strIdx:strIdx+dayIdx],ncVal[strIdx:strIdx+dayIdx],ncScale, ncOffSet,ncValUnits, ncFile)
'''

# Create loadP.nc channel loadP = gen1P + gen2P + gen3P + wtg1P + wtg2P + wtg3P + wtg4P - tes1P

loadP = np.zeros(84600)
for ncFile in ncFiles:
    if ncFile[-4:] == 'P.nc':
        nc = readNCFile(ncFile)
        ncTime = nc.time
        ncVal = nc.value
        ncScale = nc.scale
        ncOffSet = nc.offset

        if ncFile == 'tes1P.nc':
            loadP = loadP - np.asarray(ncVal)
        else:
            loadP = loadP + np.asarray(ncVal)

print(len(np.asarray(ncTime)))
ncWrt = writeNCFile(np.asarray(ncTime), loadP, 1, 0, 'kW', 'loadP.nc')