#assumes the project has already been initialized throught the UI and empty setup and component xml files exist
#String, SetupInformation - > None
def fillProjectDataFromUI(projectDir, setupInfo):
    # general imports
    import sys
    import os
    from createComponentDescriptor import createComponentDescriptor
    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)

    import pandas as pd
    from writeXmlTag import writeXmlTag
    from fillProjectComponentData import fillProjectComponentData


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

    # headerName = generalSetupInfo[headerNamevalue]
    # componentName = generalSetupInfo.componentNamevalue # a list of component names corresponding headers in timeseries data
    # componentAttribute_value = generalSetupInfo.componentAttributevalue
    # componentAttribute_unit = generalSetupInfo.componentAttributeunit
    # componentNames = generalSetupInfo.componentNamesvalue
    # writeXmlTag(projectSetup, ['componentChannels', 'headerName'], 'value', headerName, setupDir)
    # writeXmlTag(projectSetup, ['componentChannels', 'componentName'], 'value', componentName, setupDir)
    # writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'value', componentAttribute_value, setupDir)
    # writeXmlTag(projectSetup, ['componentChannels', 'componentAttribute'], 'unit', componentAttribute_unit, setupDir)

    #look for component descriptor files for all componentName
    componentDir = os.path.join(setupDir, '../Components')

    print('writing component files.')
    for component in setupInfo.components: # for each component
         print('file for %s' %component.component_name)
         createComponentDescriptor(component, componentDir)

    fillProjectComponentData(setupDir,setupInfo)


