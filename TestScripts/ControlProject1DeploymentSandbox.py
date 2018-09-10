#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:23:08 2018

@author: marcmueller-stoffels

This script runs a full simulation for the entire year. It is designed to only run baseline. That is wind and diesel
generators only, electrical and thermal storage systems are set to 0.
"""
from GBSOptimizer.optimize import optimize
from GBSModel.generateRuns import generateRuns
from GBSModel.runSimulation0 import runSimulation

import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import shutil
import os
from bs4 import BeautifulSoup as bs


# Setup
projectName = 'ControlProject1'

######## Create full base case #######

here = os.path.dirname(os.path.realpath(__file__))

rootProjectPath = os.path.join(here, '../GBSProjects/', projectName)

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
setupTagVal = ' ' #''componentNames runTimeSteps timeStep'
setupAttrVal = ' '#value value value'
componentNamesStr = ' '#ees' + str(eesIdx) + ',' + ','.join(self.baseComponents)
setupValueVal = ' '#componentNamesStr + ' ' + str(startTimeIdx) + ',' + str(endTimeIdx) + ' ' + str(1)

setAttributeSoup.setupAttributeValues.find('setupTag')['value'] = setupTagVal
setAttributeSoup.setupAttributeValues.setupAttr['value'] = setupAttrVal
setAttributeSoup.setupAttributeValues.setupValue['value'] = setupValueVal

# Make the directory for this set
setName = 'SetBaseLine'
setPath = os.path.join(rootProjectPath, 'OutputData/' + setName)
os.mkdir(setPath)
filename = projectName + setName + 'Attributes.xml'
setPathName = os.path.join(setPath, filename)
with open(setPathName, 'w') as xmlfile:
    xmlfile.write(str(setAttributeSoup))
xmlfile.close()



generateRuns(setPath)

runSimulation(setPath)

