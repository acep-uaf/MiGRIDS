# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 16:00:33 2018

@author: tcmorgan2
Reads in wind speed data from tab delimited text files.
The first portion of the file contains header information. 
The second portion contains average and standard deviation in wind speed of some time interval.
Imported files are passed through a sqlite database for temporary storage and processing.
A netCDF of raw estimated values is saved into the rawWindData folder. This file includes any gaps in data collection.
"""

import pandas as pd
import re
import logging
import sqlite3 as lite
import numpy as np
import os
from netCDF4 import Dataset
from GBSInputHandler.processInputDataFrame import processInputDataFrame

#String, String -> dataframe
def readWindData(inputDict):
    '''imports all MET data files in a folder and converts parameters to a dataframe.
    :param inputDict: [Dictionary] a dictionary containing file location, datetime and channel information
    :return: [Dictionary],[pandas.DataFrame] a dictionary of files that were read and the resulting dataframe of values is returned
    '''

    #DATETIME = 'Date & Time Stamp'
    DATETIME = inputDict['dateColumnName']
    def readAsHeader(file, header_dict, componentName):
        '''extracts the header information from a MET file.
        :param file [File] a MET file to be read.
        :param header_dict [Dictionary] a dictionary of header information
        :param componentName [String] the name of the channel of interest.
        :return [Dictionary] of header information for the file.
        '''
        inline = file.readline().split('\t')
        inline = [re.sub(r"\s+", '_', x.strip()) for x in inline] # strip whitespaces at ends and replaces spaces with underscores
        
        #assumes 'Date & Time Stamp' is the first column name where the dataframe starts. 
        #we return the dictionary of header information
        if inline[0] == DATETIME:
        
            names = inline
            return header_dict, names
        else:
            #assumes that header information for channels are prefixed with 'Channel ...'
            if inline[0][0:3] == 'Cha':
               #start a new component
               componentName = 'CH' + inline[1].rstrip()
               header_dict[componentName] = {}
            if (componentName is not None) & (len(inline) > 1):
               header_dict[componentName][inline[0].rstrip()] = inline[1].rstrip()
            return readAsHeader(file, header_dict, componentName)


    def readAsData(file, names):
        '''reast the data portion of a MET file into a dataframe
        :param file [File] the MET file to be read
        :param names [ListOf String] the channels to be read.
        :return [DataFrame] of values for specified channels with datetime index'''
        rowList = []
        for line in file:
        #these are the data lines with column names
           value_dict = {}
           cols = line.split('\t')
           for i in range(len(names)):
               value_dict[names[i]] = cols[i]

           rowList.append(value_dict)

        filedf = pd.DataFrame(rowList)
        return filedf

    #if a new channel speficication is encountered within the input files it gets incremented with an appended number
    #i.e. Channel 3 was windspeed in input file 1 but in input file 6 it becomes wind direction thus the channel name becomes CH3_1
    def channelUp(channel, existing, increment = 1) :
        newchannel = channel + '_' + str(increment)
        if newchannel not in existing.keys():
            return newchannel
        else:
            increment +=1
            return channelUp(channel, existing, increment)

    #checks it the channel input information just read in matches the information stored in the working header dictionary
    def checkMatch(channel, h, combinedHeader):
        for attribute in combinedHeader[channel].keys():

            if combinedHeader[channel][attribute]!= h[channel][attribute]:
                return False
        return True

    #adds a new channel to the combined header dictionary if it doesn't exist yet
    def addChannel(channel, h, combinedHeader, oc):

        combinedHeader[channel]={'Description':h[oc]['Description'],
                    'Height':h[oc]['Height'],
                    'Offset':h[oc]['Offset'],
                    'Scale_Factor':h[oc]['Scale_Factor'],
                    'Units':h[oc]['Units']}
        return combinedHeader

    # a data class for estimating and storing windspeed data collected at intervals
    class windRecord():
        def __init__(self, sigma=25, mu=250, minws = 0, maxws = 20, datetime = None):
            self.sigma = sigma
            self.mu = mu
            self.distribution = None
            self.minws = minws
            self.maxws = maxws
            self.datetime = datetime


        def getDatetime(self):
            return self.datetime

        #finds the previous value based on timestamp
        def getStart(self, duration, df):
            #find the wind record immediately prior to current windrecord
            previousrecordtime = self.getDatetime() - duration
            sorteddf = df.sort_values('time')
            myvalue = sorteddf['values'][sorteddf['time'] < previousrecordtime][-1:]
            if len(myvalue) > 1:
                myvalue = myvalue[0]
            elif len(myvalue) == 0:
                myvalue = None
            return myvalue

        #self, integer, numeric,string, integer
        def getValues(self, elapsed_time, start,interval, tau = None):
            mu = self.mu
            sigma = self.sigma
            timestep = pd.Timedelta(interval).seconds

            #number of records to estimate
            n = int(elapsed_time/timestep)

            #tau scales the relationship between time and change in value of x
            #larger values result in larger drift and diffusion
            if tau is None:
                tau = n

            x = np.zeros(n)
            #renormalized variables
            sigma_bis = sigma * np.sqrt(2.0 /n)
            sqrtdt = np.sqrt(timestep)

            x[0] = start
            #np.random is the random gaussian with mean 0
            for i in range(n-1):
                x[i+1] = x[i] + timestep*(-(x[i]-mu)/tau) + sigma_bis * sqrtdt * np.random.randn()

            return x


        def estimateDistribution(self, records,interval, start = None, tau = None):
           if start is None:
               start = self.minws
           tau = records
           x = self.getValues(records, start, interval, tau)

           t = pd.date_range(self.datetime - pd.to_timedelta(pd.Timedelta(interval).seconds * records, unit='s'), periods=records,freq='s')
           self.distribution = [x,t]
           return



    #a dictionary of files that are read
    fileDict = {}
    df = pd.DataFrame()
    
    for root, dirs, files in os.walk(inputDict['fileLocation']):
        for f in files:
            with open(os.path.join(root, f), 'r',errors='ignore') as file:
                #read the header information of each file
                if (file.name)[-3:] == 'txt':
                    print(file.name)
                    data = pd.DataFrame()
                    headerDict = {}

                    headerDict, names = readAsHeader(file, headerDict, None)
                    fileDict[file.name] = headerDict
                    for n in names:
                        if n not in df.columns:
                            df[n] = None
                            data[n] = None
                    #read the data from each file
                    fileData = readAsData(file, names)
                    df = pd.concat([df, fileData], axis=0, ignore_index=True)
            if file.name in fileDict.keys():
                fileDict[file.name]['rows'] = len(fileData)



    df = df.set_index(pd.to_datetime(df[DATETIME]))
    df = df.apply(pd.to_numeric, errors='ignore')
    df = df.sort_index()
    


    combinedHeader = {}
    fileLog = fileDict
    #check that there isn't mismatched header information
    for f in fileLog.keys():
        h = fileLog[f]
        rows = 0
        for channel in h.keys():
            if channel == 'rows':
                rows += h[channel]
            else:
                if channel in combinedHeader.keys():
                    #check that the values match
                    if not checkMatch(channel, h, combinedHeader):
                        addChannel(channelUp(channel, combinedHeader), h, combinedHeader, channel)
                else:
                    #add the channel
                    addChannel(channel, h, combinedHeader, channel)


    def createNetCDF(df, increment):
        # create a netcdf file
        dtype = 'float'
        # column = df.columns.values[i]
        ncName = os.path.join(inputDict['fileLocation'], (str(increment) + 'WS.nc'))
        rootgrp = Dataset(ncName, 'w', format='NETCDF4')  # create netCDF object
        rootgrp.createDimension('time', None)  # create dimension for all called time
        # create the time variable
        rootgrp.createVariable('time', dtype, 'time')  # create a var using the varnames
        rootgrp.variables['time'][:] = pd.to_timedelta(pd.Series(df.index)).values.dt.total_seconds().astype(int)

        # create the value variable
        rootgrp.createVariable('value', dtype, 'time')  # create a var using the varnames
        rootgrp.variables['value'][:] = np.array(winddf['values'])  # fill with values
        # assign attributes
        rootgrp.variables['time'].units = 'seconds'  # set unit attribute
        rootgrp.variables['value'].units = 'm/s'  # set unit attribute
        rootgrp.variables['value'].Scale = 1  # set unit attribute
        rootgrp.variables['value'].offset = 0  # set unit attribute
        # close file
        rootgrp.close()

    #now we need to fill in the gaps between sampling points
    #apply to every row, 10 minutes = 600 seconds
    def fillWindRecords(df, channels):
        database = os.path.join(inputDict['fileLocation'], 'wind.db')
        connection = lite.connect(database)

        for k in channels:
            logging.info(k)
     
            newdf = df.copy()
            newdf = newdf.sort_index()
            newColumns = [x.replace(k,'').rstrip() for x in newdf.columns]
            newdf.columns = newColumns
            valuesdf = pd.DataFrame()
            valuesdf['time'] = None
            valuesdf['values'] = None

            newdf['date'] = pd.to_datetime(newdf.index)
            #turn the df records into windrecords
            ListOfWindRecords = newdf.apply(lambda x: windRecord(x['SD'], x['Avg'], x['Min'], x['Max'], x['date']), 1)
            logging.info(len(ListOfWindRecords))
            #k is a list of values for each 10 minute interval
            recordCount = 0
            for r in ListOfWindRecords:
                #logging.info(recordCount)
                start = r.getStart(pd.Timedelta(minutes=10), valuesdf)
                recordCount +=1

                r.estimateDistribution(601,'1s',start)
                valuesdf = pd.concat([valuesdf,pd.DataFrame({'time':r.distribution[1],'values':r.distribution[0]})])
                valuesdf['values'] = valuesdf['values']
                #every 5000 records write the new values
                if recordCount%5000 == 0:
                    valuesdf.to_sql('windrecord' + k, connection, if_exists='append')
                    connection.commit()
                    valuesdf = pd.DataFrame()
                    valuesdf['time'] = None
                    valuesdf['values'] = None
            valuesdf.to_sql('windrecord' + k, connection, if_exists='append')

            winddf = pd.read_sql_query("select * from windrecord" + k, connection)

            winddf = winddf.set_index(pd.to_datetime(winddf[DATETIME], unit='s'))
            winddf = winddf[~winddf.index.duplicated(keep='first')]
            try:
                createNetCDF(winddf, k)
                connection.close()
                os.remove(database)

            except:
                print ('An error occured. Current results are stored in %s' %database)
        return winddf

    inputDict['df'] = df
    # only choose the channels desired
    winddf = processInputDataFrame(inputDict)
   
    return fileDict, winddf
