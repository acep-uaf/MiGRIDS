#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:23:08 2018

@author: marcmueller-stoffels
"""
from GBSModel.Operational.generateRuns import generateRuns
from GBSModel.Operational.runSimulation import runSimulation

import os
from bs4 import BeautifulSoup as bs
import time

# Setup
projectName = 'ControlProject1'

######## Create full base case #######

here = os.path.dirname(os.path.realpath(__file__))

rootProjectPath = os.path.join(here, '../GBSProjects/', projectName)

iterNum = 27

elapsedTime = [0]*(iterNum-1)

for i in range(1, iterNum):
    runLenghtStr = '0,' + str(i*60*60*24*7)
    # * Create the 'SetAttributes' file from the template and the specific information given
    # Load the template
    setAttributeTemplatePath = os.path.join(here, '../GBSTool/GBSModel/Resources/Setup/projectSetAttributes.xml')
    setAttributeTemplateFile = open(setAttributeTemplatePath, 'r')
    setAttributeTemplateFileXML = setAttributeTemplateFile.read()
    setAttributeTemplateFile.close()
    setAttributeSoup = bs(setAttributeTemplateFileXML, 'xml')

    # Write the project name
    setAttributeSoup.project['name'] = projectName

    # Write the power levels and duration
    compNameVal = ' ' #''ees' + str(eesIdx) + ' ees' + str(eesIdx) + ' ees' + str(eesIdx)
    compTagVal = ' ' #PInMaxPa POutMaxPa ratedDuration'
    compAttrVal = ' ' #value value value'
    #rtdDuration = int(3600*(eesEPa/eesPPa))
    compValueVal = ' ' #str(eesPPa) + ' PInMaxPa.value ' + str(rtdDuration)

    setAttributeSoup.compAttributeValues.compName['value'] = compNameVal
    setAttributeSoup.compAttributeValues.find('compTag')['value'] = compTagVal  # See issue 99 for explanation
    setAttributeSoup.compAttributeValues.compAttr['value'] = compAttrVal
    setAttributeSoup.compAttributeValues.compValue['value'] = compValueVal

    # Write additional information regarding run-time, time resolution, etc.
    setupTagVal = 'runTimeSteps' #''componentNames runTimeSteps timeStep'
    setupAttrVal = 'value'#value value value'
    componentNamesStr = ' '#ees' + str(eesIdx) + ',' + ','.join(self.baseComponents)
    setupValueVal = runLenghtStr #'0,604800'#componentNamesStr + ' ' + str(startTimeIdx) + ',' + str(endTimeIdx) + ' ' + str(1)

    setAttributeSoup.setupAttributeValues.find('setupTag')['value'] = setupTagVal
    setAttributeSoup.setupAttributeValues.setupAttr['value'] = setupAttrVal
    setAttributeSoup.setupAttributeValues.setupValue['value'] = setupValueVal

    # Make the directory for this set
    setName = 'SetPerfTest_Stitch' + str(i)
    setPath = os.path.join(rootProjectPath, 'OutputData/' + setName)
    os.mkdir(setPath)
    filename = projectName + setName + 'Attributes.xml'
    setPathName = os.path.join(setPath, filename)
    with open(setPathName, 'w') as xmlfile:
        xmlfile.write(str(setAttributeSoup))
    xmlfile.close()


    st = time.time()
    generateRuns(setPath)

    runSimulation(setPath)
    et = time.time()

    elapsedTime[i-1] = et - st

    print('Elapsed time for ' + str(i) + 'weeks is ' + str(elapsedTime[i-1]) + ' seconds')

#op = optimize('ControlProject1', [])

#op.doOptimization()