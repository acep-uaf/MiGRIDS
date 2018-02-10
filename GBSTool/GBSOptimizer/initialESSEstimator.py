# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# INITIAL ESS ESTIMATOR contains routines to preliminarily estimate the power and energy size range envelope in which to
# search for the most optimal solutions. For this, the physical limitations (maximum ramping capability, minimum start
# time) of the diesel generator fleet are used. The approach is quite brute force, but should yield a reduction in search
# range nonetheless.

from bs4 import BeautifulSoup as bs


def getTotalGrossLoad(projectPath, projectName):
    '''
    Calculates the total gross load based on available input time series. It is assumed that these input time series are
    in the prescribed netCDF format. Total gross load is defined as the real power sum of all generation assets (sources).

    :param projectSetup: [string] path to the projects 'projectSetup.xml'
    :return time: [Series] time stamps for the total load time series
    :return loadP: [Series] time series of the total load.
    '''

    # Construct path to 'projectSetup'
    projectSetup = projectPath + 'InputData/Setup/' + projectName + 'Setup.xml'
    print(projectSetup)

    # Search all 'source' assets
    projectSetupFile = open(projectSetup, "r")
    projectSetupXML = projectSetupFile.read()
    projectSetupFile.close()
    projectSoup = bs(projectSetupXML, "xml")

    for component in projectSoup.componentNames.children:
        componentPath = 'empty'
        componentSoup = []
        try:
           componentString = component.get('value')
           componentPath = projectPath + 'InputData/Components/' + componentString + 'Descriptor.xml'
           print(componentPath)
           componentFile = open(componentPath, 'r')
           componentFileXML = componentFile.read()
           componentFile.close()
           componentSoup = bs(componentFileXML, "xml")

           # Now we need to check if the component selected is a source
           if componentSoup.type.get('value') == 'source':
               print(componentString + ' is source.')
        except AttributeError: #this filters potential NavigableString issues due to spaces in XML file
           pass







    time = []
    loadP = []

    return time, loadP



time, loadP = getTotalGrossLoad('../../GBSProjects/Chevak/','Chevak')