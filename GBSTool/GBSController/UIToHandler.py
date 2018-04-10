#Is called from the GBSUserInterface package to initiate xml file generation through the GBSInputHandler functions
#SetupInformation ->

class UItoHandler():


    def userInputSetup(self, setupInfo):

        from fillProjectData import fillProjectData
        from buildProjectSetup import buildProjectSetup


        # write the information to a setup xml
        # create a mostly blank xml setup file and individual component xml files
        buildProjectSetup(setupInfo.project, setupInfo.setupFolder, setupInfo.componentNames)
        #fill in project data
        fillProjectData(setupInfo.setupFolder, setupInfo)

    #string, dictionary -> None
    #calls the InputHandler functions required to write component descriptor xml files
    def userInputComponentDescriptor(self, componentDict):
        from createComponentDescriptor import createComponentDescriptor
        from writeXmlTag import writeXmlTag
        componentDir = componentDict['filepath']
        #write the file - overwrite any existing file
        componentDescriptor = createComponentDescriptor(componentDict['name'], componentDir)

        for tag in componentDict.keys(): # for each tag (skip component name column)
            if tag not in ['name','filepath']:
                attr = 'value'
                value = componentDict[tag]
                writeXmlTag(componentDescriptor,tag,attr,value,componentDir)

        return