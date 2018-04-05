#assumes the project has already been initialized throught the UI and empty setup and component xml files exist
#String, SetupInformation - > None
def fillProjectDataFromUI(projectDir, setupInfo):
    # general imports
    import sys
    import os
    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)

    import pandas as pd
    from writeXmlTag import writeXmlTag


    # get the project directory. This is all that should be needed, since folder structure and filenames should be
    # standardized
    userInputDir = projectDir + '/InputData/Setup/UserInput/'
    if not os.path.exists(userInputDir):
        os.makedirs(userInputDir)


    projectSetup = setupInfo.project + 'Setup.xml'

    # get the directory to save the project setup xml file
    setupDir = projectDir

    #TODO make a dataframe from component info
    # next, get component information
    os.chdir(userInputDir)
    # df = pd.read_csv('componentInformation.csv') # read as a data frame
    # componentNames = setupInfo.componentNames # unique list of component names
    #
    # # get the directory to save the component descriptor xml files in
    # componentDir = projectDir + '/InputData/Components/'
    # for row in range(df.shape[0]): # for each component
    #     componentDesctiptor = componentNames[row] + 'Descriptor.xml'
    #
    #     for column in range(1,df.shape[1]): # for each tag (skip component name column)
    #         tag = df.columns[column]
    #         attr = 'value'
    #         value = df[df.columns[column]][row]
    #         writeXmlTag(componentDesctiptor,tag,attr,value,componentDir)
    #
    #     # see if there is a csv file with more tag information for that component
    #     componentTagInfo = componentNames[row] + 'TagInformation.csv'
    #     os.chdir(userInputDir)
    #     if os.path.exists(componentTagInfo):
    #         dfComponentTag = pd.read_csv(componentTagInfo)  # read as a data frame
    #         dfComponentTag = dfComponentTag.fillna('')  # remplace nan values with empty'
    #         componetTag = dfComponentTag.as_matrix()  # matrix of values from data frame
    #         # fill tag information into the component descriptor xml file
    #         for row in range(componetTag.shape[0]):  # for each tag
    #             tag = componetTag[row, range(0, 4)]
    #             tag = [x for x in tag if not x == '']
    #             attr = dfComponentTag['Attribute'][row]
    #             value = dfComponentTag['Value'][row]
    #             writeXmlTag(componentDesctiptor, tag, attr, value, componentDir)
    # ########################
    # fill in the data from the general setup information csv file above

    #create a dictionary to create xml tags from.
    generalSetupInfo = setupInfo.getSetupTags()

    for k in generalSetupInfo.keys():  # for each component
        #read a components tag info
        tag = k
        for v in generalSetupInfo[k].keys():
            attr = v
            value = generalSetupInfo[k][v]
            writeXmlTag(projectSetup, tag, attr, value, setupDir)

    # get component timeseries  information
    os.chdir(userInputDir)

    headerName = setupInfo.headerNames
    componentName = setupInfo.componentNames # a list of component names corresponding headers in timeseries data
    componentAttribute_value = setupInfo.attributes
    componentAttribute_unit = setupInfo.units
    writeXmlTag(projectSetup, ['componentChannels', 'headerName'], 'value', headerName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentName'], 'value', componentName, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'value', componentAttribute_value, setupDir)
    writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'unit', componentAttribute_unit, setupDir)