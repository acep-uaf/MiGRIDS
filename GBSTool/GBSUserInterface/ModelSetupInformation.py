'''SetupInformation is a data model for storing setup information collected through the SetupWizard or UISetupForm.
The information is written to an XML file using the writeXML method. '''
from GBSInputHandler.Component import Component
from GBSController.UIToHandler import UIToHandler
import os
#setup tags are a class that is used for attributes that get written to the setup.xml
class SetupTag:
    def __init__(self, n, v = None):
        self.name = n
        self.value = v

    def assignValue(self,v):
        self.value = v

    def assignUnits(self,v):
        self.unit = v

    def assignFormat(self, v):
        self.format = v

    def assign(self,method,v):
        method(self,v)

    def getDict(self):
        d = {}
        for k in self.__dict__.keys():
            if self.__getattribute__(k) is not None:
                d[k] = self.__getattribute__(k)
        return d


class ModelSetupInformation:

    def __init__(self):
        #dictionary of dialog card names and their corresponding assignment functions
        #TODO make dynamic based on WizardTree names
        self.functionDictionary = {'project':self.assignProject,
                                   'inputFileFormatvalue':[self.assignInputFileFormat,SetupTag.assignValue],
                                   'windFileDirvalue':[self.assignWindFileDir,SetupTag.assignValue],
                                   'hydroFileDirvalue':[self.assignHydroFileDir,SetupTag.assignValue],
                                   'inputFileDirvalue':[self.assignInputFileDir,SetupTag.assignValue],
                                   'inputFileTypevalue':[self.assignInputFileType, SetupTag.assignValue],
                                   'dateChannelformat':[self.assignDateChannel,SetupTag.assignFormat],
                                   'dateChannelvalue': [self.assignDateChannel, SetupTag.assignValue],
                                   'inputTimeStepvalue':[self.assignInputTimeStep,SetupTag.assignValue],
                                   'timeStepvalue':[self.assignTimeStep, SetupTag.assignValue],
                                   'inputTimeStepunit':[self.assignInputTimeStep,SetupTag.assignUnits],
                                   'timeStepunit': [self.assignTimeStep, SetupTag.assignUnits],
                                   'realLoadChannelvalue':[self.assignLoadChannel,SetupTag.assignValue],
                                   'realLoadChannelunit': [self.assignLoadChannel, SetupTag.assignUnits],
                                   'timeChannelformat': [self.assignTimeChannel, SetupTag.assignFormat],
                                   'timeChannelvalue': [self.assignTimeChannel, SetupTag.assignValue],
                                   'componentNamesvalue':[self.assignComponentNames, SetupTag.assignValue],
                                   'componentNamevalue': [self.assignComponentName, SetupTag.assignValue],
                                   'headerNamevalue': [self.assignHeaderName, SetupTag.assignValue],
                                   'componentAttributevalue': [self.assignComponentAttribute, SetupTag.assignValue],
                                   'componentAttributeunit': [self.assignComponentAttribute, SetupTag.assignUnits]

                                   }



        #empty values
        self.components =[]
        self.project =''
        self.data = None
        self.inputFileDir = SetupTag('inputFileDir')
        self.windFileDir = SetupTag('windFileDir')
        self.hydroFileDir = SetupTag('hydroFileDir')
        self.inputFileType = SetupTag('inputFileType')
        self.inputFileFormat= SetupTag('inputFileFormat')
        self.dateChannel = SetupTag('dateChannel')
        self.timeChannel = SetupTag('timeChannel')
        self.realLoadChannel = SetupTag('realLoadChannel')
        self.inputFileFormat = SetupTag('inputFileFormat')
        self.inputFileType = SetupTag('inputFileType')
        self.inputTimeStep = SetupTag('inputTimeStep')
        self.timeStep = SetupTag('timeStep')
        self.inputFileDir = SetupTag('inputFileDir')
        self.componentNames = SetupTag('componentNames')
        self.headerName = SetupTag('headerName')
        self.componentName = SetupTag('componentName')
        self.componentAttribute = SetupTag('componentAttribute')

    def getAttributes(self):
        return self.__dict__.keys()

    # but this will likely change to perform some actions during parameter assigment.
    # That is why each parameter has its own fuction
    def assignProject(self, name):

        self.project = name

        if 'setupFolder' not in self.__dict__.keys():
            path = os.path.dirname(__file__)
            self.setupFolder = os.path.join(path, '../../GBSProjects/', self.project, 'InputData/Setup')
        self.componentFolder = os.path.join(self.setupFolder ,'../Components')
        self.projectFolder = os.path.join(self.setupFolder, '../../' )
        self.outputFolder = os.path.join(self.projectFolder, 'OutputData')

        #if there isn't a setup folder then its a new project
        if not os.path.exists(self.setupFolder):
            #make the project folder
            os.makedirs(self.setupFolder)
        if not os.path.exists(self.componentFolder):
            #make the component
            os.makedirs(self.componentFolder)

    def assignInputFileType(self,m,v):
        self.inputFileType.assign(m,v)

    def assignSetupFolder(self, setupFile):
        import os
        self.setupFolder = os.path.dirname(setupFile)
        self.assignProject(os.path.basename(setupFile[:-9]))

    def assignComponentNames(self, m, v):
        # string gets split to list
        if type(v) is str:
            v = v.split()
        elif type(v) is list:
            #unfilled list items need to be filled with NA
            v = [f if f != '' else 'NA' for f in v]

        self.componentNames.assign(m,v)

    def assignComponentName(self, m,v):
        # string gets split to list
        if type(v) is str:
            v = v.split()
        elif type(v) is list:
            #unfilled list items need to be filled with NA
            v = [f if f != '' else 'NA' for f in v]
        self.componentName.assign(m, v)

    def assignHeaderName(self, m, v):
        #string gets split to list
        if type(v) is str:
            v = v.split()
        elif type(v) is list:
            # unfilled list items need to be filled with NA
            v = [f if f != '' else 'NA' for f in v]
        self.headerName.assign(m, v)

    def assignComponentAttribute(self,m,v):
        # string gets split to list
        if type(v) is str:
            v = v.split()
        elif type(v) is list:
            #unfilled list items need to be filled with NA
            v = [f if f != '' else 'NA' for f in v]
        self.componentAttribute.assign(m,v)


    def assignLoadChannel(self,m,v):
        self.realLoadChannel.assign(m,v)


    def assignInputFileFormat(self, m,v):
        self.inputFileFormat.assign(m,v)

    def assignInputTimeStep(self, m, v):
        self.inputTimeStep.assign(m, v)

    def assignTimeStep(self, m, v):
        self.timeStep.assign(m, v)

    def assignWindFileDir(self,m,v):
        self.windFileDir.assign(m,v)

    def assignHydroFileDir(self,m,v):
        self.hydroFileDir.assign(m,v)

    def assignInputFileDir(self,m,v):
        self.inputFileDir.assign(m,v)

    def assignDateChannel(self, m,v):
        self.dateChannel.assign(m,v)

    def assignTimeChannel(self, m, v):
        self.timeChannel.assign(m, v)


    #string, string ->
    def assign(self, dialog, value):

        #if the dialog has a subheading pass the subheading to a SetupTag function
        if dialog in self.functionDictionary.keys():
            method = self.functionDictionary[dialog]
            if type(method) is list:
                method[0](method[1],value)
            else:
                method(value)

    #return the file path for a set attribute xml file for a given set
    #String -> String
    def getSetAttributeXML(self, set):
        filePath = os.path.join(self.outputFolder, set, self.project + set + 'Attributes.xml')
        return filePath

    #creates a dictionary designed to feed into fillProjectData
    #->dictionary
    def getSetupTags(self):

        d = {}
        #for all the attributes that are of type SetupTag add their name and values to a dictionary
        for a in self.__dict__.keys():

            v = self.__getattribute__(a)
            if type(v) == SetupTag:
                if v.getDict() is not None:
                    d[v.name]=v.getDict()

        return d
    # #make a new component and add it to the component list
    # def makeNewComponent(self,component,originalHeading,units,attribute,componentType):
    #     # start a component with basic info or original header name, component name and type and attribute
    #     newComponent = Component(component=component,originalHeading = originalHeading, units=units,attribute=attribute,
    #                              componentType=componentType)
    #     self.addComponent(newComponent)
    # #delete a component from a component list
    # def removeComponent(self,component):
    #     self.components = [x for x in self.components if x != component]
    # #add a component to the component list
    # def addComponent(self, newComponent):
    #     self.component.append(newComponent)

    #read setup xml and assign values to the model parameters
    def feedSetupInfo(self):
        import os
        handler = UIToHandler()

        if (self.project is None) | (self.project == ''):
            return False
        if not os.path.exists(self.setupFolder):
            return False
        # tell the controller to tell the InputHandler to read the xml and set the model values
        handler.inputHandlerToUI(self.setupFolder, self)

        return True
    #write a new setup xml file for this project
    def writeNewXML(self):

        #tell controller to tell InputHandler package to write input xmls
        handler = UIToHandler()
        handler.makeSetup(self)
        return True