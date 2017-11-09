# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 3, 2017
# License: MIT License (see LICENSE file of this package for more information)

# fill in information about the project into the descriptor and setup xml files
def fillProjectData(projectName,componentDir,setupDir):
    # general imports
    import tkinter as tk
    from tkinter import filedialog
    import pandas as pd
    from writeXmlTag import writeXmlTag
    import numpy as np
    import os

    # TODO: some sore of GUI to get data from user
    # for now get data from csv files
    # first get component information
    print('Choose the csv file where the component information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName) # read as a data frame

    for row in range(df.shape[0]): # for each component
        componentName = df['componentName'][row]
        componentDesctiptor = componentName + 'Descriptor.xml'
        for column in range(1,df.shape[1]): # for each tag (skip component name column)
            tag = df.columns[column]
            attr = 'value'
            value = df[df.columns[column]][row]
            writeXmlTag(componentDesctiptor,tag,attr,value,componentDir)


    # get component timeserires  information
    print('Choose the csv file where the component time series information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName) # read as a data frame
    projectSetup = projectName+'Setup.xml'


    headerName = list(df['headerName'])
    componentName = list(df['componentName'])
    componentAttribute_value = list(df['componentAttribute_value'])
    componentAttribute_unit = list(df['componentAttribute_unit'])
    writeXmlTag(projectSetup, ['componentChannels', 'headerName'], 'value', headerName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentName'], 'value', componentName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'value', componentAttribute_value, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'unit', componentAttribute_unit, setupDir)

    # get other time series information
    print('Choose the csv file where other setup information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName)  # read as a data frame
    df=df.fillna('') # remplace nan values with empty
    projectSetup = projectName + 'Setup.xml'

    A = df.as_matrix()
    for row in range(A.shape[0]):  # for each component
        tag = A[row,range(0,4)]
        tag = [x for x in tag if not x == '']
        attr = df['Attribute'][row]
        value = df['Value'][row]
        writeXmlTag(projectSetup,tag,attr,value,setupDir)
