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

    #look for component descriptor files for all componentName
    componentDir = os.path.join(setupDir, '../Components')

    #component is a string
    for component in setupInfo.componentNames.value: # for each component

         #if there isn't a component descriptor file create one
         if not os.path.exists(os.path.join(componentDir, component + 'Descriptor.xml')):
             createComponentDescriptor(component, componentDir)




