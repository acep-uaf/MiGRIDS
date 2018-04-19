#Is called from the GBSUserInterface package to initiate xml file generation through the GBSInputHandler functions
#SetupInformation ->

class UIToHandler():
    #generates an setup xml file based on information in a SetupInformation object
    #SetupInformation -> None
    def makeSetup(self, setupInfo):

        from fillProjectData import fillProjectData
        from buildProjectSetup import buildProjectSetup

        # write the information to a setup xml
        # create a mostly blank xml setup file
        buildProjectSetup(setupInfo.project, setupInfo.setupFolder, setupInfo.componentNames)
        #fill in project data into the setup xml and create descriptor xmls if they don't exist
        fillProjectData(setupInfo.setupFolder, setupInfo)
        return

    #string, string -> Soup

    #calls the InputHandler functions required to write component descriptor xml files
    def makeComponentDescriptor(self, component,componentDir):
        from makeSoup import makeSoup

        #returns either a template soup or filled soup

        componentSoup = makeSoup(component, componentDir)

        return componentSoup

    #pass a component name, component folder and soup object to be written to a component descriptor
    #string, string, soup -> None
    def writeSoup(self, component, fileDir, soup):
        from createComponentDescriptor import createComponentDescriptor
        #soup is an optional argument, without it a template xml will be created.
        createComponentDescriptor(component, fileDir, soup)
        return

    #fill a single tag for an existing component descriptor file
    #dictionary, string -> None
    def updateComponentDiscriptor(self, componentDict, tag):
        from writeXmlTag import writeXmlTag
        attr = 'value'
        value = componentDict[tag]
        writeXmlTag(componentDict['component_name'] + 'Descriptor.xml', tag, attr, value, componentDict['filepath'])
        return
    #delete a descriptor xml from the project component folder
    #String, String -> None
    def removeDescriptor(self,componentName, componentDir):
        print ('component name %s will be deleted once this is implemented' %componentName)
        return
    #return a list of component descriptor files in a component directory
    #String -> List
    def findDescriptors(self,componentDir):
        import os

        directories = []
        for file in os.listdir(componentDir):
            if file.endswith('.xml'):

                directories.append(file)
        return directories
    #copy an existing xml file to the current project director and write contents to SQLRecord to update component_manager database
    #string, string, SQLRecord -> SQLRecord
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
        #get the soup and write the xml
        soup = self.makeComponentDescriptor(temporaryComponent,componentDir)
        sqlRecord = self.updateDescriptor(soup, sqlRecord)
        return sqlRecord

    def updateDescriptor(self,soup,sqlRecord):#fill the record
        sqlRecord.setValue('component_type',soup.findChild('component')['name'][0:3])

        sqlRecord.setValue('component_name',soup.findChild('component')['name'])

        sqlRecord.setValue('pinmaxpa',soup.findChild('PInMaxPa')['value'])
        sqlRecord.setValue('qoutmaxpa',soup.findChild('QOutMaxPa')['value'])
        sqlRecord.setValue('qinmaxpa',soup.findChild('QInMaxPa')['value'])
        sqlRecord.setValue('isvoltagesource',soup.findChild('isVoltageSource')['value'])

        return sqlRecord