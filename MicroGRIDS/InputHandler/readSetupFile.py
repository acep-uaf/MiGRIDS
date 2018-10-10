# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 17:53:34 2018

@author: tcmorgan2
"""
import os
from InputHandler.getUnits import getUnits
from Analyzer.DataRetrievers.readXmlTag import readXmlTag

def readSetupFile(fileName):
    ''' Reads a setup.xml file and creates a dictionary of attributes used during the data import process.
    :param: filename [String] a file path to a setup.xml file.
    :return [dictionary] containing attributes needed for loading data.'''
    try:
        # project name
        projectName = readXmlTag(fileName,'project','name')[0]
        setupDir = os.path.dirname(fileName)
        # input specification
        inputDictionary = {}
        #filelocation is the raw timeseries file.
        #if multiple files specified look for raw_wind directory
        # input a list of subdirectories under the GBSProjects directory

        inputDictionary['setupDir'] = setupDir
        
        lol = readXmlTag(fileName,'inputFileDir','value')
        inputDictionary['fileLocation'] = [os.path.join(setupDir,'..','..','..',*l) if l[0] == projectName else l for l in lol ]
    
    
        # file type
        inputDictionary['fileType'] = readXmlTag(fileName,'inputFileType','value')
        
        inputDictionary['outputInterval'] = readXmlTag(fileName,'timeStep','value')
        inputDictionary['outputIntervalUnit'] = readXmlTag(fileName,'timeStep','unit')
        inputDictionary['runTimeSteps'] = readXmlTag(fileName,'runTimeSteps','value')
        
        # get date and time values
        inputDictionary['dateColumnName'] = readXmlTag(fileName,'dateChannel','value')
        inputDictionary['dateColumnFormat'] = readXmlTag(fileName,'dateChannel','format')
        inputDictionary['timeColumnName'] = readXmlTag(fileName,'timeChannel','value')
        inputDictionary['timeColumnFormat'] = readXmlTag(fileName,'timeChannel','format')
        inputDictionary['utcOffsetValue'] = readXmlTag(fileName,'inputUTCOffset','value')
        inputDictionary['utcOffsetUnit'] = readXmlTag(fileName,'inputUTCOffset','unit')
        inputDictionary['dst'] = readXmlTag(fileName,'inputDST','value')
        inputDictionary['timeZone'] = readXmlTag(fileName,'timeZone','value')
        inputDictionary['componentName']= readXmlTag(fileName, 'componentName','value')
        flexibleYear = readXmlTag(fileName,'flexibleYear','value')
        
        # convert string to bool
        inputDictionary['flexibleYear'] = [(x.lower() == 'true') | (x.lower() == 't') for x in flexibleYear]
        
        for idx in range(len(inputDictionary['outputInterval'])): # there should only be one output interval specified
            if len(inputDictionary['outputInterval']) > 1:
                inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][idx]
            else:
                inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][0]
        
        
        # get data units and header names
        inputDictionary['columnNames'], inputDictionary['componentUnits'], \
        inputDictionary['componentAttributes'],inputDictionary['componentNames'], inputDictionary['useNames'] = getUnits(projectName,setupDir)
    except Exception as e:
        print(e)
        return
    return inputDictionary


                