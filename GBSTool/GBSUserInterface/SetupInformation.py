'''SetupInformation is a data model for storing setup information collected through the SetupWizard or UISetupForm.
The information is written to an XML file using the writeXML method. '''
from Component import Component


class SetupTag:
    def __init__(self, n, v = None):
        self.name = n
        self.value = v

    def assignValue(self,v):
        self.value = v

    def assignUnits(self,v):
        self.units = v

    def assignFormat(self, v):
        self.format = v

    def assign(self,method,v):
        method(self,v)

    def getDict(self):
        d = {}
        for k in self.__dict__.keys():
            d[k] = self.__getattribute__(k)
        return d


class SetupInformation:
    from Component import Component
    def __init__(self):
        #dictionary of dialog card names and their corresponding assignment functions
        #TODO make dynamic based on WizardTree names
        self.functionDictionary = {'project':self.assignProject,
                                   'inputFileformat':self.assignFileFormat,
                                   'windFileDirvalue':self.assignWindFolder,
                                   'hydroFileDirvalue':self.assignHydroFolder,
                                   'inputFileDirvalue':self.assignTimeseriesFolder,
                                   'dateChannelformat':[self.assignDateChannel,SetupTag.assignFormat],
                                   'dateChannelvalue': [self.assignDateChannel, SetupTag.assignValue],
                                   'inputTimeStepvalue':[self.assignInputTimeStep,SetupTag.assignValue],
                                   'outputTimeStepvalue':[self.assignOutputTimeStep,SetupTag.assignValue],
                                   'inputTimeStepunit':[self.assignInputTimeStep,SetupTag.assignUnits],
                                   'outputTimeStepunit': [self.assignOutputTimeStep, SetupTag.assignUnits],
                                   'realLoadChannelvalue':[self.assignLoadChannel,SetupTag.assignValue],
                                   'realLoadChannelunit': [self.assignLoadChannel, SetupTag.assignUnits],
                                   'timeChannelformat': [self.assignTimeChannel, SetupTag.assignFormat],
                                   'timeChannelvalue': [self.assignTimeChannel, SetupTag.assignValue],

                                   }


        self.componentNames = ['wtg1P']
        self.headerNames = []
        self.project =''
        self.inputDir = ''
        self.attributes = []
        self.units = []
        self.dateChannel = SetupTag('dateChannel')
        self.timeChannel = SetupTag('timeChannel')
        self.realLoadChannel = SetupTag('realLoadChannel')
        self.inputFileFormat = SetupTag('inputFileFormat')
        self.inputFileType = SetupTag('inputFileType')
        self.inputTimeStep = SetupTag('inputTimeStep')
        self.outputTimeStep = SetupTag('outputTimeStep')
        self.inputFileDir = SetupTag('inputFileDir')

        #components is a list of component class objects
        #the type of class determines how the information will be written to an xml
        self.components = []


    #TODO currently each assignment just assigns a parameter, but this will likely change to perform some actions during parameter assigment. That is why each parameter has its own fuction
    def assignProject(self, name):
        import os
        self.project = name
        fileDir = os.getcwd()

        self.setupFolder = os.path.join(fileDir,'../../GBSProjects',self.project, 'InputData/Setup')

    def assignLoadChannel(self,m,v):
        self.realLoadChannel.assign(m,v)

    def assignHeaderNames(self,name):
        self.headerNames = name

    def assignFileFormat(self, name):
        self.dataFormat = name

    def assignInputTimeStep(self, m, v):
        self.inputTimeStep.assign(m, v)

    def assignOutputTimeStep(self,m, v):
        self.outputTimeStep.assign(m, v)

    def assignWindFolder(self, name):
        self.WindFolder = name

    def assignHydroFolder(self, name):
        self.HydroFolder = name

    def assignTimeseriesFolder(self, name):
        self.TimeSeriesFolder = name

    def assignDateChannel(self, m,v):
        self.dateChannel.assign(m,v)

    def assignTimeChannel(self, m, v):
        self.timeChannel.assign(m, v)

    def assignAttributes(self, name):
        self.attributes = name
    def assignUnits(self,name):
        self.units = name
    #string, string ->
    def assign(self, dialog, value):

        #if the dialog has a subheading pass the subheading to a SetupTag function
        if dialog in self.functionDictionary.keys():
            method = self.functionDictionary[dialog]
            if type(method) is list:
                method[0](method[1],value)
            else:
                method(value)

    #creates a dictionary designed to feed into fillProjectData
    #->dictionary
    def getSetupTags(self):

        d = {}
        #for all the attributes that are of type SetupTag add their name and values to a dictionary
        for a in self.__dict__.keys():

            v = self.__getattribute__(a)
            if type(v) == SetupTag:
                d[v.name]=v.getDict()

        print(d)
        return d
    #make a new component and add it to the component list
    def makeNewComponent(self,component,originalHeading,units,attribute,componentType):
        # start a component with basic info or original header name, component name and type and attribute
        newComponent = Component(component=component,originalHeading = originalHeading, units=units,attribute=attribute,
                                 componentType=componentType)
        self.addComponent(newComponent)
    #delete a component from a component list
    def removeComponent(self,component):
        self.components = [x for x in self.components if x != component]
    #add a component to the component list
    def addComponent(self, newComponent):
        self.component.append(newComponent)

    #read setup xml and assign values to the model parameters
    def feedSetupInfo(self):
        from inputHandlerToUI import inputHandlerToUI

        fileDir = self.setupFolder

        # tell the controller to tell the InputHandler to read the xml and set the model values
        inputHandlerToUI(fileDir, self)

        return True
    #write a new setup xml file for this project
    def writeNewXML(self):
        from UIToHandler import UIToHandler
        #tell controller to tell InputHandler package to write input xmls
        handler = UIToHandler()
        handler.makeSetup(self)
        return True