'''SetupInformation is a data model for storing setup information collected through the SetupWizard or UISetupForm.
The information is written to an XML file using the writeXML method. '''
from InputHandler.Component import Component
from Controller.UIToHandler import UIToHandler
from UserInterface.getFilePaths import getFilePath
import os
#setup tags are a class that is used for attributes that get written to the setup.xml
class SetupTag:
    def __init__(self, n, v = None):
        self.name = n
        self.value = v

    def assignValue(self,v,**kwargs):
        position = kwargs.get("position")
        if type(v) is list:
            if ('value' in self.__dict__.keys()):
                if (self.value is None) | (self.value == ""):
                    self.value = v
                elif len(self.value) < 1:
                    self.value = v
                elif (position is not None) & (type(self.value) is list):
                       if  (position < len(self.value)):
                           self.value[position] = v[0]
                       else:
                           self.value = self.value + v
                else:
                    self.value = self.value + v
        else:
            self.value = v
        return

    def assignUnits(self,v,**kwargs):
        position = kwargs.get("position")
        if type(v) is list:
            if ('unit' in self.__dict__.keys()):
                if (self.unit is None) | (self.unit == ""):
                    self.unit = v
                elif (position is not None):
                    if (position < len(self.unit)):
                        self.unit[position] = v[0]
                    else:
                        self.unit = self.unit + v

                else:
                    self.unit = self.unit + v
            else:
                self.unit = v

    def assignFormat(self, v,**kwargs):
        position = kwargs.get("position")

        if type(v) is list:
            if ('format' in self.__dict__.keys()):
                if (self.format is None) | (self.format == ""):
                    self.format = v
                elif (position is not None):
                    if (position < len(self.format)):
                        self.format[position] = v[0]
                    else:
                        self.format = self.format + v

                else:
                    self.format = self.format + v
            else:
                self.format = v

    def assign(self,method,v,**kwargs):

        method(self,v,**kwargs)

    def getDict(self):
        d = {}
        for k in self.__dict__.keys():
            if self.__getattribute__(k) is not None:
                d[k] = self.__getattribute__(k)
        return d

def stringToList(v):
    if type(v) is str:
        v = v.split()
    elif type(v) is list:
        #unfilled list items need to be filled with NA
        v = [f if f != '' else 'NA' for f in v]
    return v

class ModelSetupInformation:

    def __init__(self):
        #dictionary of dialog card names and their corresponding assignment functions
        #TODO make dynamic based on WizardTree names
        self.functionDictionary = {'project':self.assignProject,
                                   'inputFileFormatvalue':[self.assignInputFileFormat,SetupTag.assignValue],
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
                                   'componentAttributeunit': [self.assignComponentAttribute, SetupTag.assignUnits],
                                   'timeZonevalue':[self.assignTimeZone, SetupTag.assignValue],
                                   'useDST':[self.assignUseDST,SetupTag.assignValue]
                                   }

        #empty values
        self.componentFolder = ''

        self.project =''
        self.data = None
        self.components=[]
        self.setupFolder = ''
        self.inputFileType = SetupTag('inputFileType')
        self.inputFileFormat= SetupTag('inputFileFormat')
        self.dateChannel = SetupTag('dateChannel')
        self.timeChannel = SetupTag('timeChannel')
        self.realLoadChannel = SetupTag('realLoadChannel')
        self.inputFileFormat = SetupTag('inputFileFormat')
        self.inputFileType = SetupTag('inputFileType')
        self.inputTimeStep = SetupTag('inputTimeStep')
        self.timeZone = SetupTag('timeZone')
        self.useDST = SetupTag('useDST')
        self.runTimesteps = SetupTag('runTimeStep')
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
        #setupFolder is in tags before it gets set.
        if ('setupFolder' not in self.__dict__.keys()) | (self.setupFolder == ""):
            path = os.path.dirname(__file__)
            self.setupFolder = os.path.join(path, *['..','..','GBSProjects', self.project, 'InputData','Setup'])
        self.componentFolder = getFilePath(self.setupFolder ,'Components')
        self.projectFolder = getFilePath(self.setupFolder, 'Project')
        #self.outputFolder = getFilePath(self.projectFolder, 'OutputData')

        #if there isn't a setup folder then its a new project
        if not os.path.exists(self.setupFolder):
            #make the project folder
            os.makedirs(self.setupFolder)
        if not os.path.exists(self.componentFolder):
            #make the component
            os.makedirs(self.componentFolder)


    def assignSetupFolder(self, setupFile):
        import os
        self.setupFolder = os.path.dirname(setupFile)
        self.assignProject(os.path.basename(setupFile[:-9]))

    def assignComponentNames(self, m, v,**kwargs):
        #self.componentNames.assign(m,stringToList(v),**kwargs)
        self.componentNames.assign(m, v, **kwargs)
    def assignComponentName(self, m,v,**kwargs):
        self.componentName.assign(m, stringToList(v),**kwargs)

    def assignHeaderName(self, m, v,**kwargs):
        v = stringToList(v)
        v = [i.replace(' ', '_') for i in v]
        self.headerName.assign(m, v,**kwargs)

    def assignComponentAttribute(self,m,v,**kwargs):
        self.componentAttribute.assign(m,stringToList(v),**kwargs)

    def assignLoadChannel(self,m,v,**kwargs):
        self.realLoadChannel.assign(m,stringToList(v),**kwargs)

    def assignInputFileType(self, m, v,**kwargs):
        self.inputFileType.assign(m, stringToList(v),**kwargs)

    def assignInputFileFormat(self, m,v,**kwargs):
        self.inputFileFormat.assign(m,stringToList(v),**kwargs)

    def assignInputTimeStep(self, m, v,**kwargs):
        self.inputTimeStep.assign(m, stringToList(v),**kwargs)

    def assignRunTimesteps(self,m,v,**kwargs):
        self.runTimesteps.assign(m,stringToList(v),**kwargs)

    def assignTimeStep(self, m, v,**kwargs):
        self.timeStep.assign(m, stringToList(v),**kwargs)

    def assignTimeZone(self,m,v,**kwargs):
        self.timeZone.assign(m,stringToList(v),**kwargs)

    def assignUseDST(self,m,v,**kwargs):
        self.useDST.assign(m,stringToList(v),**kwargs)

    def assignInputFileDir(self,m,v,**kwargs):
        self.inputFileDir.assign(m,stringToList(v),**kwargs)

    def assignDateChannel(self, m,v,**kwargs):
        self.dateChannel.assign(m,stringToList(v),**kwargs)

    def assignTimeChannel(self, m, v,**kwargs):
        self.timeChannel.assign(m, stringToList(v),**kwargs)

    #assign value to setup tag attribute
    #string, string -> None
    def assign(self, dialog, value,**kwargs):
        position = kwargs.get("position")
        #if the dialog has a subheading pass the subheading to a SetupTag function
        if dialog in self.functionDictionary.keys():
            method = self.functionDictionary[dialog]
            if type(method) is list:
                method[0](method[1],value,position=position)
            else:
                method(value,position=position)

    #return the file path for a set attribute xml file for a given set
    #String -> String
    def getSetAttributeXML(self, set):
        filePath = os.path.join(getFilePath(self.setupFolder, set),set + 'Attributes.xml')
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
    #make a new component and add it to the component list
    def makeNewComponent(self,component,originalHeading,units,attribute,componentType):
        # start a component with basic info or original header name, component name and type and attribute
        newComponent = Component(component_name=component,column_name = component + attribute, original_field_name = originalHeading, units=units,attribute=attribute,
                                 type=componentType)
        self.addComponent(newComponent)
    #delete a component from a component list
    def removeComponent(self,component):
        self.components = [x for x in self.components if x != component]
    #add a component to the component list
    def addComponent(self, newComponent):
        if self.components is None:
            self.components = [newComponent]
            return
        self.components.append(newComponent)
        return
    def setComponents(self,loC):
        ''' sets a list of Components to the components attribute
        :param loC [List Of Components] a list of Component objects'''
        self.components = loC
        return

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