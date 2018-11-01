

# imports
import os
import sqlite3
import sys
import re
import numpy as np
import pandas as pd
import pickle
import glob
from MicroGRIDS.Analyzer.PerformanceAnalyzers.getFuelUse import getFuelUse
from bs4 import BeautifulSoup as Soup
import os
from MicroGRIDS.Analyzer.CurveAssemblers.genFuelCurveAssembler import GenFuelCurve
from MicroGRIDS.Analyzer.DataRetrievers.readNCFile import readNCFile
from MicroGRIDS.Analyzer.DataWriters.writeNCFile import writeNCFile
import pandas as pd
import pickle
import numpy as np

def getRunFuelUse(projectSetDir,runs='all'):
    # get the set number
    dir_path = os.path.basename(projectSetDir)
    setID = str(dir_path[3:])

    # check which runs to analyze
    if runs == 'all':
        os.chdir(projectSetDir)
        runDirs = glob.glob('Run*/')
        runs = [x[3:] for x in runDirs]

    # iterate through each run
    for runNum in runs:
        # get run dir
        runDir = os.path.join(projectSetDir, 'Run' + str(runNum))
        componentsDir = os.path.join(runDir, 'Components')
        # go to outputData dir and find all generator output nc files
        outputDataDir = os.path.join(runDir, 'OutputData')
        os.chdir(outputDataDir)
        genOutFileNames = glob.glob('gen*PSet*Run*.nc')
        # get the generator names
        genNames = [x.split('PSet')[0] for x in genOutFileNames]
        # initiate the fuel curves and power output
        fuelCurveDataPoints = pd.DataFrame(columns=['fuelCurve_pPu', 'fuelCurve_massFlow', 'POutMaxPa'], index=genNames)
        genAllP = pd.DataFrame(columns=['time'] + [x + 'P' for x in genNames])
        for idxGen, genName in enumerate(genNames):
            # read xml file
            genDescriptor = genName + 'Set' + setID + 'Run' + str(runNum) + 'Descriptor.xml'
            os.chdir(componentsDir)
            genDescriptorFile = open(genDescriptor, "r")
            genDescriptorXml = genDescriptorFile.read()
            genDescriptorFile.close()
            genSoup = Soup(genDescriptorXml, "xml")
            # get get max output
            fuelCurveDataPoints['POutMaxPa'][genName] = float(genSoup.POutMaxPa.get('value'))  # nameplate capacity

            # get the generator fuel curve
            # Handle the fuel curve interpolation
            fuelCurveDataPoints['fuelCurve_pPu'][genName] = genSoup.fuelCurve.pPu.get('value')
            fuelCurveDataPoints['fuelCurve_massFlow'][genName] = genSoup.fuelCurve.massFlow.get('value')

            # load the generator output
            os.chdir(outputDataDir)
            genOutFile = readNCFile(genName + 'PSet' + setID + 'Run' + str(runNum) + '.nc')
            genAllP[genName + 'P'] = genOutFile.value[:] * genOutFile.scale + genOutFile.offset

            if idxGen == 0:
                genAllP.time = genOutFile.time[:]

        genAllFuelUsed, fuelStats = getFuelUse(genAllP, fuelCurveDataPoints, interpolationMethod='linear')

        # save netcdf files of fuel use
        for genName in genNames:
            os.chdir(outputDataDir)
            # convert back from kg to kg/s
            writeNCFile(np.array(genAllP.time), np.array(genAllFuelUsed[genName])/genAllP['time'].diff(), 1, 0, 'kg/s',
                    genName + 'FuelConsSet' + setID + 'Run' + str(runNum) + '.nc')
        """
        # save results in the sql database and the csv file
        os.chdir(projectSetDir)
        conn = sqlite3.connect('set' + setID + 'Results.db')
        # get the previously saved results
        dfResult = pd.read_sql_query('select * from Results', conn)
        # insert
        dfResult.to_sql('Results', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        conn.close()
        dfResult.to_csv('Set' + str(setNum) + 'Results.csv')  # save a csv version"""