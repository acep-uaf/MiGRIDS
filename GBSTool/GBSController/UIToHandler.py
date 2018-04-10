#Is called from the GBSUserInterface package to initiate xml file generation through the GBSInputHandler functions
#SetupInformation ->

class UIToHandler():


    def makeSetup(self, setupInfo):

        from fillProjectData import fillProjectData
        from buildProjectSetup import buildProjectSetup


        # write the information to a setup xml
        # create a mostly blank xml setup file and individual component xml files
        buildProjectSetup(setupInfo.project, setupInfo.setupFolder, setupInfo.componentNames)
        #fill in project data
        fillProjectData(setupInfo.setupFolder, setupInfo)

    #string, dictionary -> None
    #calls the InputHandler functions required to write component descriptor xml files
    def makeComponentDescriptor(self, componentDict):
        from createComponentDescriptor import createComponentDescriptor
        from writeXmlTag import writeXmlTag
        componentDir = componentDict['filepath']
        #write the file - overwrite any existing file
        componentDescriptor = createComponentDescriptor(componentDict['name'], componentDir)

        for tag in componentDict.keys(): # for each tag (skip component name column)
            if tag not in ['component_name','filepath']:
                attr = 'value'
                value = componentDict[tag]
                writeXmlTag(componentDescriptor,tag,attr,value,componentDir)

        return

    #fill a single tag for an existing component descriptor file
    #dictionary, string -> None
    def fillComponentDiscriptor(self, componentDict, tag):
        from writeXmlTag import writeXmlTag
        attr = 'value'
        value = componentDict[tag]
        writeXmlTag(componentDict['component_name'] + 'Descriptor.xml', tag, attr, value, componentDict['filepath'])
        return