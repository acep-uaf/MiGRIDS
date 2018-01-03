# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 3, 2017
# License: MIT License (see LICENSE file of this package for more information)

# fill in information about the project into the descriptor and setup xml files
def fillProjectData():
    # general imports
    import tkinter as tk
    from tkinter import filedialog
    import pandas as pd
    from writeXmlTag import writeXmlTag
    from buildComponentDescriptor import buildComponentDescriptor
    from buildProjectSetup import buildProjectSetup
    import numpy as np
    import os

    # TODO: some sore of GUI to get data from user
    # for now get data from csv files
    # first, get general project setup information
    print('Choose the csv file where general setup information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName)  # read as a data frame
    df = df.fillna('')  # remplace nan values with empty
    # grab data from csv to be used in writing other csv files
    projectName = df['Value'][df['Tag1']=='project'].values[0]
    projectSetup = projectName + 'Setup.xml'
    # get the directory to save the project setup xml file
    print('Choose a directory to save the xml project setup file in.')
    root = tk.Tk()
    root.withdraw()
    setupDir = filedialog.askdirectory()
    generalSetupInfo = df.as_matrix() # this is written to the projectSetup.xml file below, after it is initialized
    generalSetupInfoDf = df

    # next, get component information
    print('Choose the csv file where the component information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName) # read as a data frame
    componentNames = list(df['componentName']) # unique list of component names
    # get the directory to save the component descriptor xml files in
    print('Choose a directory to save the xml component descriptor files in.')
    root = tk.Tk()
    root.withdraw()
    componentDir = filedialog.askdirectory()
    for row in range(df.shape[0]): # for each component
        componentDesctiptor = componentNames[row] + 'Descriptor.xml'
        # initialize the component descriptor xml file
        buildComponentDescriptor([componentNames[row]],componentDir)
        for column in range(1,df.shape[1]): # for each tag (skip component name column)
            tag = df.columns[column]
            attr = 'value'
            value = df[df.columns[column]][row]
            writeXmlTag(componentDesctiptor,tag,attr,value,componentDir)

    # initialize project setup xml file
    buildProjectSetup(projectName,setupDir,componentNames)
    # fill in the data from the general setup information csv file above
    for row in range(generalSetupInfo.shape[0]):  # for each component
        tag = generalSetupInfo[row, range(0, 4)]
        tag = [x for x in tag if not x == '']
        attr = generalSetupInfoDf['Attribute'][row]
        value = generalSetupInfoDf['Value'][row]
        writeXmlTag(projectSetup, tag, attr, value, setupDir)
    # get component timeserires  information
    print('Choose the csv file where the component time series information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName) # read as a data frame
    projectSetup = projectName+'Setup.xml'
    headerName = list(df['headerName'])
    componentName = list(df['componentName']) # a list of component names corresponding headers in timeseries data
    componentAttribute_value = list(df['componentAttribute_value'])
    componentAttribute_unit = list(df['componentAttribute_unit'])
    writeXmlTag(projectSetup, ['componentChannels', 'headerName'], 'value', headerName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentName'], 'value', componentName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'value', componentAttribute_value, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'unit', componentAttribute_unit, setupDir)


