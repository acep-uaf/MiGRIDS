
#String- > None
def fillProjectDataFromCSV(projectDir):
    '''
    fills in information about the project into the descriptor and setup xml files.
    :param projectDir: [String] the directory containing information needed to generate the project xml files
    :return:
    '''
    # general imports
    # add to sys path
    import sys
    import os
    import pandas as pd
    from InputHandler.writeXmlTag import writeXmlTag
    from InputHandler.buildAllComponentDescriptor import buildComponentDescriptor
    from InputHandler.buildProjectSetup import buildProjectSetup

    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)

    userInputDir = os.path.join(projectDir, *['InputData','Setup','UserInput'])

    os.chdir(userInputDir)

    df = pd.read_csv('generalTagInformation.csv')  # read as a data frame
    df = df.fillna('')  # remplace nan values with empty
    # grab data from csv to be used in writing other csv files
    projectName = df['Value'][df['Tag1']=='project'].values[0]
    projectSetup = projectName + 'Setup.xml'

    # get the directory to save the project setup xml file
    setupDir = os.path.join(projectDir, *['InputData','Setup'])
    generalSetupInfo = df.as_matrix() # this is written to the projectSetup.xml file below, after it is initialized
    generalSetupInfoDf = df

    # next, get component information
    os.chdir(userInputDir)
    df = pd.read_csv('componentInformation.csv') # read as a data frame
    componentNames = list(df['componentName']) # unique list of component names

    # get the directory to save the component descriptor xml files in
    componentDir = os.path.join(projectDir, *['InputData','Components'])
    for row in range(df.shape[0]): # for each component
        componentDesctiptor = componentNames[row] + 'Descriptor.xml'
        # initialize the component descriptor xml file
        buildComponentDescriptor([componentNames[row]],componentDir)

        for column in range(1,df.shape[1]): # for each tag (skip component name column)
            tag = df.columns[column]
            attr = 'value'
            value = df[df.columns[column]][row]
            writeXmlTag(componentDesctiptor,tag,attr,value,componentDir)

        # see if there is a csv file with more tag information for that component
        componentTagInfo = componentNames[row] + 'TagInformation.csv'
        os.chdir(userInputDir)
        if os.path.exists(componentTagInfo):
            dfComponentTag = pd.read_csv(componentTagInfo)  # read as a data frame
            dfComponentTag = dfComponentTag.fillna('')  # remplace nan values with empty'
            componetTag = dfComponentTag.as_matrix()  # matrix of values from data frame
            # fill tag information into the component descriptor xml file
            for row in range(componetTag.shape[0]):  # for each tag
                tag = componetTag[row, range(0, 4)]
                tag = [x for x in tag if not x == '']
                attr = dfComponentTag['Attribute'][row]
                value = dfComponentTag['Value'][row]
                writeXmlTag(componentDesctiptor, tag, attr, value, componentDir)

    # initialize project setup xml file - basically empty but contains component names
    buildProjectSetup(projectName,setupDir,componentNames)
    # fill in the data from the general setup information csv file above
    for row in range(generalSetupInfo.shape[0]):  # for each component
        tag = generalSetupInfo[row, range(0, 4)]
        tag = [x for x in tag if not x == '']
        attr = generalSetupInfoDf['Attribute'][row]
        value = generalSetupInfoDf['Value'][row]
        writeXmlTag(projectSetup, tag, attr, value, setupDir)

    # get component timeseries  information
    os.chdir(userInputDir)
    df = pd.read_csv('timeSeriesInformation.csv') # read as a data frame
    headerName = list(df['headerName'])
    componentName = list(df['componentName']) # a list of component names corresponding headers in timeseries data
    componentAttribute_value = list(df['componentAttribute_value'])
    componentAttribute_unit = list(df['componentAttribute_unit'])
    writeXmlTag(projectSetup, ['componentChannels', 'headerName'], 'value', headerName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentName'], 'value', componentName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'value', componentAttribute_value, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'unit', componentAttribute_unit, setupDir)

    return
