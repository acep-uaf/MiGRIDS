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
    #comonentDict is a dictionary containing values for a specific component.
    #calls the InputHandler functions required to write component descriptor xml files
    def makeComponentDescriptor(self, component,componentDir):
        from makeSoup import makeSoup
        #returns either a template soup or filled soup
        componentSoup = makeSoup(component, componentDir)

        return componentSoup
    #pass a soup object to be written to a component descriptor
    def writeSoup(self, component, fileDir, soup):
        from createComponentDescriptor import createComponentDescriptor

        createComponentDescriptor(component, fileDir, soup)

    #fill a single tag for an existing component descriptor file
    #dictionary, string -> None
    def fillComponentDiscriptor(self, componentDict, tag):
        from writeXmlTag import writeXmlTag
        attr = 'value'
        value = componentDict[tag]
        writeXmlTag(componentDict['component_name'] + 'Descriptor.xml', tag, attr, value, componentDict['filepath'])
        return

    def removeDescriptor(self,componentName, componentDir):
        print ('component name %s will be deleted once this is implemented' %componentName)
        return

    def findDescriptors(self,componentDir):
        import os
        from Component import Component
        directories = []
        for file in os.listDir(componentDir):
            if file.endswith('.xml'):
                newComponent = Component(component_type=file[0:3])
                soup = self.makeComponentDescriptor(newComponent,componentDir)
                directories.append(soup)
        return directories

    def copyDescriptor(self,descriptorFile, componentDir, sqlRecord):
        import os
        import shutil
        from Component import Component
        fileName =os.path.basename(descriptorFile)
        componentType = fileName[0:3]
        componentName = fileName[:-14]
        # copy the xml to the project folder
        try:
            shutil.copy2(descriptorFile, componentDir)
        except shutil.SameFileError:
            print('This descriptor file already exists in this project')
        temporaryComponent = Component(component_name= componentName, type=componentType)
        #get the soup
        soup = self.makeComponentDescriptor(temporaryComponent,componentDir)
        #fill the record
        sqlRecord.setValue('component_type',soup.findChild('component')['name'][0:3])

        #the name gets set with the sql trigger
        #sqlRecord.setValue('component_name',componentName)
        sqlRecord.setValue('pinmaxpa',soup.findChild('PInMaxPa')['value'])
        sqlRecord.setValue('qoutmaxpa',soup.findChild('QOutMaxPa')['value'])
        sqlRecord.setValue('qinmaxpa',soup.findChild('QInMaxPa')['value'])
        sqlRecord.setValue('isvoltagesource',soup.findChild('isVoltageSource')['value'])

        return sqlRecord