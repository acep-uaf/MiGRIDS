# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 21, 2017
# License: MIT License (see LICENSE file of this package for more information)

# write a value to an xml tag
def getUnits(projectName,projectDir):
    # general imports
    from readXmlTag import readXmlTag
    import numpy as np

    fileName = projectName + 'Setup.xml'

    headerTag = ['componentChannels','headerName']
    headerAttr = 'value'
    headerNames = readXmlTag(fileName,headerTag,headerAttr,projectDir)

    attrTag = ['componentChannels','componentAttribute']
    attrAttr = 'unit'
    componentUnits = readXmlTag(fileName, attrTag, attrAttr, projectDir)

    attrTag = ['componentChannels', 'componentAttribute']
    attrAttr = 'value'
    componentAttributes = readXmlTag(fileName, attrTag, attrAttr, projectDir)

    nameTag = ['componentChannels', 'componentName']
    nameAttr = 'value'
    componentNames = readXmlTag(fileName, nameTag, nameAttr, projectDir)

    newHeaderNames = np.core.defchararray.add(componentNames,
                                           componentAttributes)  # create column names to replace existing headers

    return headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames
