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

        # fill in the data from the general setup information csv file above

    #get a dictionary of tags
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

    #look for component descriptor files for all componentName
    componentDir = os.path.join(setupDir, '../Components')


    for component in setupInfo.componentNames: # for each component
         componentDescriptor = component + 'Descriptor.xml'
         file = os.path.join(componentDir,componentDescriptor)
         #don't do anything if the file exists.
         if not file.is_file():
             #otherwise create the file
             buildComponentDescriptor(componentDescriptor, componentDir)


