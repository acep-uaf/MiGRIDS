#assumes the project has already been initialized throught the UI and empty setup and component xml files exist
#String, ModelSetupInformation - > None
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





    projectSetup = setupInfo.project + 'Setup.xml'


    #get a dictionary of tags from xml
    generalSetupInfo = setupInfo.getSetupTags()

    for k in generalSetupInfo.keys():  # for each component
        #read a components tag info
        tag = k
        for v in generalSetupInfo[k].keys():
            attr = v
            value = generalSetupInfo[k][v]
            writeXmlTag(projectSetup, tag, attr, value, setupInfo.setupFolder)


    #look for component descriptor files for all componentName
    componentDir = os.path.join(setupInfo.setupFolder, '../Components')

    #component is a string
    if setupInfo.componentNames.value is not None:
        for component in setupInfo.componentNames.value: # for each component

             #if there isn't a component descriptor file create one
             if not os.path.exists(os.path.join(componentDir, component + 'Descriptor.xml')):
                 createComponentDescriptor(component, componentDir)




