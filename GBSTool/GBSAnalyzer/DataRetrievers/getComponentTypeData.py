# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: February 27, 2018
# License: MIT License (see LICENSE file of this package for more information)

from bs4 import BeautifulSoup as bs
import pandas as pd

def getComponentTypeData(projectPath, projectName, componentType):
    '''
    Retrieves all meta-data for a given component class from the descriptor xml files.

    :param projectPath: [string] path to the projects root folder
    :param projectName: [string] the project name as it is used in <projectName>Setup.xml
    :param componentType: [String] the abbreviated component type descriptor, e.g. 'gen' to retrieve all generators
    :return componentData: [DataFrame] Contains component information with XML tags as columns and component names
    (gen1, gen2, etc) as index.
    '''

    # Load pertinent information from project xml files
    # Setup status message bin
    msg = []

    # Construct path to 'projectSetup'
    projectSetup = projectPath + 'InputData/Setup/' + projectName + 'Setup.xml'
    msg.append('Project path: ' + projectSetup)

    # Get list of all components
    projectSetupFile = open(projectSetup, "r")
    projectSetupXML = projectSetupFile.read()
    projectSetupFile.close()
    projectSoup = bs(projectSetupXML, "xml")
    components = projectSoup.componentNames.get("value").split()
    msg.append('Project components found: ' + ' '.join(components))

    index = list()
    componentSoupBowl = list()
    # Iterate through components and check if they are of componentType.
    for cmpnt in components:
        if cmpnt.startswith(componentType):
            componentString = cmpnt
            componentPath = projectPath + 'InputData/Components/' + componentString + 'Descriptor.xml'
            msg.append('Loading: ' + componentPath)
            componentFile = open(componentPath, 'r')
            componentFileXML = componentFile.read()
            componentFile.close()
            componentSoup = bs(componentFileXML, "xml")

            index.append(componentSoup.component.get('name'))
            componentSoupBowl.append(componentSoup)


    # Step through each componentType descriptor and construct the DF from it.
    componentData = pd.DataFrame([], index)

    # First we'll construct the column names - note that we only want columns with tag names that carry actual values.
    # Hence, if a tag merely is a container of further tags, it is pitched.
    for child in componentSoupBowl[0].component.find_all():

        # If the child has further children tags, add these to the column name
        if child.parent != componentSoupBowl[0].component:
            colName = child.parent.name + '_' + child.name
        else:
            colName = child.name

        # Now retrieve the values for this column
        val = []
        if child.get('value') != None:
            val.append(child.get('value'))
            for j in range(1, len(componentSoupBowl)):
                val.append(componentSoupBowl[j].component.find(child.name).get('value'))
            componentData[colName] = val

    return componentData
