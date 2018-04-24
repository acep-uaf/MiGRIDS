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
        import os

        if os.path.exists(os.path.join(componentDir,componentName + 'Descriptor.xml')):
             os.remove(os.path.join(componentDir,componentName + 'Descriptor.xml'))
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
    #copy an existing xml file to the current project director and write contents to SQLRecord to update project_manager database
    #string, string, SQLRecord -> SQLRecord
    def copyDescriptor(self,descriptorFile, componentDir, sqlRecord):
        import os
        import shutil
        from Component import Component
        fileName =os.path.basename(descriptorFile)

        componentName = fileName[:-14]
        # copy the xml to the project folder
        try:
            shutil.copy2(descriptorFile, componentDir)
        except shutil.SameFileError:
            print('This descriptor file already exists in this project')

        #get the soup and write the xml
        soup = self.makeComponentDescriptor(componentName,componentDir)
        sqlRecord = self.updateDescriptor(soup, sqlRecord)
        return sqlRecord

    #updates the values in a sqlrecord with attributes in soup
    #Beautiful Soup, SQLRecord -> SQlRecord
    def updateDescriptor(self,soup,sqlRecord):#fill the record
        sqlRecord.setValue('component_type',soup.findChild('component')['name'][0:3])

        sqlRecord.setValue('component_name',soup.findChild('component')['name'])

        sqlRecord.setValue('pinmaxpa',soup.findChild('PInMaxPa')['value'])
        sqlRecord.setValue('qoutmaxpa',soup.findChild('QOutMaxPa')['value'])
        sqlRecord.setValue('qinmaxpa',soup.findChild('QInMaxPa')['value'])
        sqlRecord.setValue('isvoltagesource',soup.findChild('isVoltageSource')['value'])

        return sqlRecord

    #use the input handler to load raw timeseries data, fix data and return fixed data
    #String, String, String -> DataClass
    def loadFixData(self, setupFile):
        print(setupFile)
        import os
        from getUnits import getUnits
        from readDataFile import readDataFile
        from fixBadData import fixBadData
        from readXmlTag import readXmlTag

        Village = readXmlTag(setupFile, 'project', 'name')[0]
        # input specification
        # input specification can be for multiple input files or a single file in AVEC format.
        inputSpecification = readXmlTag(setupFile, 'inputFileFormat', 'value')[0]
        # filelocation is the raw timeseries file.
        # if multiple files specified look for raw_wind directory
        # input a list of subdirectories under the GBSProjects directory
        fileLocation = readXmlTag(setupFile, 'inputFileDir', 'value')
        fileLocation = os.path.join(*fileLocation)
        fileLocation = os.path.join('../../GBSProjects', fileLocation)
        # file type
        fileType = readXmlTag(setupFile, 'inputFileType', 'value')[0]
        outputInterval = readXmlTag(setupFile, 'outputTimeStep', 'value')[0] + \
                         readXmlTag(setupFile, 'outputTimeStep', 'unit')[0]
        inputInterval = readXmlTag(setupFile, 'inputTimeStep', 'value')[0] + \
                        readXmlTag(setupFile, 'inputTimeStep', 'unit')[0]

        # get data units and header names
        headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames = getUnits(Village, os.path.dirname(setupFile))

        # read time series data, combine with wind data if files are seperate.

        df, listOfComponents = readDataFile(inputSpecification, fileLocation, fileType, headerNames, newHeaderNames,
                                            componentUnits,
                                            componentAttributes)  # dataframe with time series information. replace header names with column names

        # now fix the bad data

        df_fixed = fixBadData(df, os.path.dirname(setupFile), listOfComponents, inputInterval)


        # fix the intervals
        from fixDataInterval import fixDataInterval
        df_fixed_interval = fixDataInterval(df_fixed, outputInterval)

        d = {}
        for c in listOfComponents:
           d[c.component_name] = c.toDictionary()


        return df_fixed_interval, d

    #dataframe of cleaned data
    #generate netcdf files for model running
    #dataframe, dictionary -> None
    def createNetCDF(self, df,componentDict,varNames, setupFile):
        from dataframe2netcdf import dataframe2netcdf
        from readXmlTag import readXmlTag
        import os
        inputDirectory = readXmlTag(setupFile, 'inputFileDir', 'value')
        inputDirectory = os.path.join(*inputDirectory)
        outputDirectory = os.path.join(inputDirectory, '/ProcessedData')
        #it there isn't an output directory make one
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)

        dataframe2netcdf(df.fixed, componentDict, None, outputDirectory)
        return
    #Object, string -> None
    def storeData(self,df,setupFile):
        from readXmlTag import readXmlTag
        import os
        import pickle
        inputDirectory = readXmlTag(setupFile, 'inputFileDir', 'value')
        inputDirectory = os.path.join(*inputDirectory)
        outputDirectory = os.path.join(inputDirectory, '/ProcessedData')
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'processed_input_file.pkl')
        file = open(outfile,'wb')
        pickle.dump(df,file)
        file.close()
        return