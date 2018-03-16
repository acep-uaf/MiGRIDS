'''
Handles retrieving wind power data from Igiugig DB and stuffing into single channel wtgXP.nc files.

@author marc_mueller-stoffels
'''

import sqlite3 as lite
import os
from GBSTool.GBSInputHandler.dataframe2netcdf import dataframe2netcdf as df2nc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime
import time


def handleTime(connection):
    '''
    The time stamps in the DB unfortunately are organized as textual data. This makes retrieval and handling a bit more
    costly.
    :param connection:
    :return timeStamps: [list] UNIX epoch style time.
    '''

    # Pull time column from DB
    windtime = pd.read_sql_query("select time from igiugig_wind_power", connection)

    # Convert to datetime objects
    timeDF = [datetime.datetime.strptime(elem, '%Y-%m-%d %H:%M:%S') for elem in windtime.iloc[:,0]]

    # Convert to unix epochs
    timeStamps = [elem.timestamp() for elem in timeDF]

    return timeStamps

def handleWindSpeed(connection):
    '''
    Loads the wind speed data from the DB
    :param connection:
    :return windspeed: [dataframe] wind speeds in m/s
    '''

    windspeed = pd.read_sql_query("select windspeed_ms from igiugig_wind_power", connection)

    return windspeed





database = os.path.join('/Users/marcmueller-stoffels/Downloads','igiugig.db')
connection = lite.connect(database)
print('Database connection established.')

t = time.time()
timeS = handleTime(connection)
elapsed = time.time() - t
t = time.time()
print('Time stamps loaded. Time to load and process: ' + str(elapsed) + ' s')



ws = handleWindSpeed(connection)
elapsed = time.time() - t
t = time.time()
print('Wind speeds loaded. Time to load and process: ' + str(elapsed) + ' s')

# Create dataframe to hand to netCDF file generator.
d = {'time':timeS, 'value':ws.iloc[:,0]}
df = pd.DataFrame(d)

df2nc(df,'m/s',[1,1],[0,0], ['windspeed'], '/Users/marcmueller-stoffels/Documents/GBSToolsGit/GBSProjects/Igiugig/InputData/TimeSeriesData/ProcessedData')
print('Wind speed file generated.')

# Clean up to ease up on memory usage.
df = []
d = []
ws = []

for i in range(1,23):
    t = time.time()
    label = 'wtg' + str(i) + 'P'
    print('Retrieving channel: ' + label)
    query = "select wtg" + str(i) + "P from igiugig_wind_power"
    var = pd.read_sql_query(query, connection)

    # make usable dataframe
    d = {'time': timeS, 'value': var.iloc[:,0]}
    df = pd.DataFrame(d)

    df2nc(df,'kW', [1,1], [0,0], [label], '/Users/marcmueller-stoffels/Documents/GBSToolsGit/GBSProjects/Igiugig/InputData/TimeSeriesData/ProcessedData')
    elapsed = time.time() - t

    # Clean up
    d = []
    df = []

    print(label + '.nc created. Time elapsed :' + str(elapsed) + ' s.')
