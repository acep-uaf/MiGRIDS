#Is called from the GBSUserInterface package to initiate xml file generation through the GBSInputHandler functions
#ModelSetupInformation ->

import os
import pickle
import pandas as pd
from PyQt5 import QtWidgets
from bs4 import BeautifulSoup
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.InputHandler.buildProjectSetup import buildProjectSetup
from MiGRIDS.InputHandler.fillProjectData import fillProjectData
from MiGRIDS.InputHandler.makeSoup import makeComponentSoup
from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag
from MiGRIDS.InputHandler.mergeInputs import mergeInputs
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getFilePaths import getFilePath




class UIToHandler():
    #generates an setup xml file based on information in a ModelSetupInformation object
    #ModelSetupInformation -> None
    def makeSetup(self, setupInfo):
       # write the information to a setup xml
        # create a mostly blank xml setup file, componentNames is a SetupTag class so we need the value
        buildProjectSetup(setupInfo.project, setupInfo.setupFolder, setupInfo.componentNames.value)
        #fill in project data into the setup xml and create descriptor xmls if they don't exist
        fillProjectData(setupInfo.setupFolder, setupInfo)
        return

    #string, string -> Soup
    #calls the InputHandler functions required to write component descriptor xml files
    def makeComponentDescriptor(self, component,componentDir):
         #returns either a template soup or filled soup
        componentSoup = makeComponentSoup(component, componentDir)
        return componentSoup

    #pass a component name, component folder and soup object to be written to a component descriptor
    #string, string, soup -> None
    def writeComponentSoup(self, component, fileDir, soup):
        from GBSInputHandler.createComponentDescriptor import createComponentDescriptor
        #soup is an optional argument, without it a template xml will be created.
        createComponentDescriptor(component, fileDir, soup)
        return

    #fill a single tag for an existing component descriptor file
    #dictionary, string -> None
    def updateComponentDiscriptor(self, componentDict, tag):
        attr = 'value'
        value = componentDict[tag]
        writeXmlTag(componentDict['component_name'] + 'Descriptor.xml', tag, attr, value, componentDict['filepath'])
        return

    #delete a descriptor xml from the project component folder
    #String, String -> None
    def removeDescriptor(self,componentName, componentDir):
        if os.path.exists(os.path.join(componentDir,componentName + 'Descriptor.xml')):
             os.remove(os.path.join(componentDir,componentName + 'Descriptor.xml'))
        return

    #return a list of component descriptor files in a component directory
    #String -> List
    def findDescriptors(self,componentDir):
        directories = []
        for file in os.listdir(componentDir):
            if file.endswith('.xml'):

                directories.append(file)
        return directories

    #copy an existing xml file to the current project director and write contents to SQLRecord to fillSetInfo project_manager database
    #string, string, SQLRecord -> SQLRecord
    def copyDescriptor(self,descriptorFile, componentDir, sqlRecord):
        import shutil

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

        from GBSInputHandler.getUnits import getUnits
        from GBSInputHandler.fixBadData import fixBadData
        from GBSInputHandler.fixDataInterval import fixDataInterval

        inputDictionary = {}
        Village = readXmlTag(setupFile, 'project', 'name')[0]
        # input specification


        # input a list of subdirectories under the GBSProjects directory
        fileLocation = readXmlTag(setupFile, 'inputFileDir', 'value')
        #fileLocation = os.path.join(*fileLocation)
        #fileLocation = os.path.join('/', fileLocation)
        #inputDictionary['fileLocation'] = [os.path.join('../../GBSProjects', *x) for x in fileLocation]
        inputDictionary['fileLocation'] = fileLocation
        # file type
        fileType = readXmlTag(setupFile, 'inputFileType', 'value')
        outputInterval = readXmlTag(setupFile, 'timeStep', 'value') + \
                         readXmlTag(setupFile, 'timeStep', 'unit')
        inputInterval = readXmlTag(setupFile, 'inputTimeStep', 'value') + \
                        readXmlTag(setupFile, 'inputTimeStep', 'unit')
        inputDictionary['timeZone'] = readXmlTag(setupFile,'timeZone','value')
        inputDictionary['fileType'] = readXmlTag(setupFile, 'inputFileType', 'value')
        inputDictionary['outputInterval'] = readXmlTag(setupFile, 'timeStep', 'value')
        inputDictionary['outputIntervalUnit'] = readXmlTag(setupFile, 'timeStep', 'unit')
        inputDictionary['inputInterval'] = readXmlTag(setupFile, 'inputTimeStep', 'value')
        inputDictionary['inputIntervalUnit'] = readXmlTag(setupFile, 'inputTimeStep', 'unit')
        inputDictionary['runTimeSteps'] = readXmlTag(setupFile,'runTimeSteps','value')
        # get date and time values
        inputDictionary['dateColumnName'] = readXmlTag(setupFile, 'dateChannel', 'value')
        inputDictionary['dateColumnFormat'] = readXmlTag(setupFile, 'dateChannel', 'format')
        inputDictionary['timeColumnName'] = readXmlTag(setupFile, 'timeChannel', 'value')
        inputDictionary['timeColumnFormat'] = readXmlTag(setupFile, 'timeChannel', 'format')
        inputDictionary['utcOffsetValue'] = readXmlTag(setupFile, 'inputUTCOffset', 'value')
        inputDictionary['utcOffsetUnit'] = readXmlTag(setupFile, 'inputUTCOffset', 'unit')
        inputDictionary['dst'] = readXmlTag(setupFile, 'inputDST', 'value')
        flexibleYear = readXmlTag(setupFile, 'flexibleYear', 'value')
        inputDictionary['flexibleYear'] = [(x.lower() == 'true') | (x.lower() == 't') for x in flexibleYear]

        #combine values with their units as a string
        for idx in range(len(inputDictionary['outputInterval'])):  # there should only be one output interval specified
            if len(inputDictionary['outputInterval']) > 1:
                inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][idx]
            else:
                inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][0]

        for idx in range(len(inputDictionary['inputInterval'])):  # for each group of input files
            if len(inputDictionary['inputIntervalUnit']) > 1:
                inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][idx]
            else:
                inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][0]

        # get data units and header names
        inputDictionary['columnNames'], inputDictionary['componentUnits'], \
        inputDictionary['componentAttributes'], inputDictionary['componentNames'], inputDictionary['useNames'] = getUnits(Village, os.path.dirname(setupFile))

        # read time series data, combine with wind data if files are seperate.
        df, listOfComponents = mergeInputs(inputDictionary)

        # check the timespan of the dataset. If its more than 1 year ask for / look for limiting dates
        minDate = min(df.index)
        maxDate = max(df.index)
        limiters = inputDictionary['runTimeSteps']

        if ((maxDate - minDate) > pd.Timedelta(days=365)) & (limiters ==['all']):
             newdates = self.DatesDialog(minDate, maxDate)
             m = newdates.exec_()
             if m == 1:
               
                #inputDictionary['runTimeSteps'] = [newdates.startDate.text(),newdates.endDate.text()]
                inputDictionary['runTimeSteps'] = [pd.to_datetime(newdates.startDate.text()), pd.to_datetime(newdates.endDate.text())]
                #TODO write to the setup file so can be archived

        # now fix the bad data
        df_fixed = fixBadData(df,os.path.dirname(setupFile),listOfComponents,inputDictionary['inputInterval'],inputDictionary['runTimeSteps'])

        # fix the intervals
        print('fixing data timestamp intervals to %s' %inputDictionary['outputInterval'])
        df_fixed_interval = fixDataInterval(df_fixed, inputDictionary['outputInterval'])
        df_fixed_interval.preserve(os.path.dirname(setupFile))
        return df_fixed_interval, listOfComponents

    class DatesDialog(QtWidgets.QDialog):

        def __init__(self,minDate,maxDate):
            super().__init__()
            self.setWindowTitle("Dates to Analyze")
            grp = QtWidgets.QGroupBox()
            hz = QtWidgets.QVBoxLayout()
            prompt = QtWidgets.QLabel("Select Dates to Analyze")
            hz.addWidget(prompt)
            box = QtWidgets.QHBoxLayout()
            self.startDate = QtWidgets.QDateEdit()
            self.startDate.setObjectName('start')
            self.startDate.setDisplayFormat('yyyy-MM-dd')
            self.startDate.setDate(minDate)
            self.startDate.setCalendarPopup(True)
            self.endDate = QtWidgets.QDateEdit()
            self.endDate.setDate(maxDate)
            self.endDate.setObjectName('end')
            self.endDate.setDisplayFormat('yyyy-MM-dd')
            self.endDate.setCalendarPopup(True)
            box.addWidget(self.startDate)
            box.addWidget(self.endDate)
            grp.setLayout(box)
            hz.addWidget(grp)

            buttonBox = QtWidgets.QDialogButtonBox()
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok
                             | QtWidgets.QDialogButtonBox.Cancel)
            buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
            buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
            hz.addWidget(buttonBox)

            self.setLayout(hz)

            def getValues(self):
                a,b = self.startDate.text(), self.endDate.text()
                return a,b
    #List Of dataframe of cleaned data
    #generate netcdf files for model running
    #dataframe, dictionary -> None
    def createNetCDF(self, lodf,componentDict,setupFolder):
        from GBSInputHandler.dataframe2netcdf import dataframe2netcdf
        outputDirectory = getFilePath(setupFolder, 'Processed')
        netCDFList = []
        #if there isn't an output directory make one
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        #only the largest dataframe is kept
        largest = 0
        for i, df in enumerate(lodf):
            if len(df) > largest:
                netCDFList = dataframe2netcdf(df, componentDict, outputDirectory)
                largest = len(df)
        return netCDFList

    #save the components for a project
    #List of Components, String -> None
    def storeComponents(self, ListOfComponents,setupFile):
        outputDirectory = os.path.dirname(setupFile)

        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'components.pkl')
        file = open(outfile, 'wb')
        pickle.dump(ListOfComponents, file)
        file.close()
        return
    #save the DataClass object as a pickle in the processed data folder
    #DataClass, string -> None
    def storeData(self,df,setupFile):

        outputDirectory = getFilePath(os.path.dirname(setupFile), 'Processed')
        print("processed data saved to %s: " %outputDirectory)
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'processed_input_file.pkl')
        file = open(outfile,'wb')
        pickle.dump(df,file)
        file.close()
        return

    #read in a pickled data object if it exists
    #string->DataClass
    def loadInputData(self,setupFile):

        outputDirectory = os.path.join(os.path.dirname(setupFile), *['..','TimeSeriesData','Processed'])
        outfile = os.path.join(outputDirectory, 'processed_input_file.pkl')

        if not os.path.exists(outfile):
            return None

        file = open(outfile, 'rb')
        data = pickle.load(file)
        file.close()
        return data
    #string->ListOfComponents
    #loads a pickled Component list
    def loadComponents(self, setupFile):
        outputDirectory = os.path.dirname(setupFile)
        infile = os.path.join(outputDirectory, 'components.pkl')
        if not os.path.exists(infile):
            return

        file = open(infile, 'rb')
        loC = pickle.load(file)
        file.close()
        return loC
    #generates all the set and run folders in the output directories and starts the sequence of models running
    #String, ComponentTable, SetupInformation
    def runModels(self, currentSet, componentTable, setupInfo):
        from PyQt5 import QtWidgets
        from GBSModel.Operational.generateRuns import generateRuns
        from GBSUserInterface.makeAttributeXML import makeAttributeXML, writeAttributeXML
        from GBSModel.Operational.runSimulation import runSimulation
        #generate xml's based on inputs
        #call to run models

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Starting Models",
                                    "You won't beable to edit data while models are running. Are you sure you want to continue?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()
        #generate the setAttributes xml file
        soup = makeAttributeXML(currentSet,componentTable)
        setDir = os.path.join(setupInfo.projectFolder,'OutputData',currentSet.capitalize())
        fileName = setupInfo.project + currentSet.capitalize() + 'Attributes.xml'

        writeAttributeXML(soup,setDir,fileName)

        # Check if a set component attribute database already exists
        if os.path.exists(os.path.join(setDir, currentSet + 'ComponentAttributes.db')):
            #ask to delete it or generate a new set
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Overwrite files?",
                                        "Set up files were already generated for this model set. Do you want to overwrite them? ")
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            result = msg.exec()

            if result == QtWidgets.QMessageBox.Yes:
                os.remove(os.path.join(setDir, currentSet + 'ComponentAttributes.db'))
            else:
                #create a new set tab
                return

        #if it does delete it.
        #generate run folders from attributes xml
        generateRuns(setDir)

        #now start running models
        runSimulation(projectSetDir=setDir)

    def inputHandlerToUI(self, setupFolder, setupInfo):
        from GBSInputHandler.getSetupInformation import getSetupInformation
        # assign tag values in the setupxml to the setupInfo model
        getSetupInformation(os.path.join(setupFolder, setupInfo.project + 'Setup.xml'), setupInfo)
        return

    # creates a soup object from set attribute xml file
    # ->soup
    def getSetAttributeXML(self, xmlFile):
        #read the attributes xml
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

        return soup
    def getComponentTypes(self):
        dbhandler = ProjectSQLiteHandler()
        loT = dbhandler.getComponentTypes()
        dbhandler.closeDatabase()
        return loT