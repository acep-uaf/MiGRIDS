'''SetupInformation is a data model for storing setup information collected through the SetupWizard or UISetupForm.
The information is written to an XML file using the writeXML method. '''


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
        print(method)
        print(v)
        method(self,v)

    def getDict(self):
        d = {}
        for k in self.__dict__.keys():
            d[k] = self.__getattribute__(k)
        return d
# class FormatValue(SetupTag):
#     def __init__(self, n, v= None, f = None):
#         super().__init__(n,v, f)
#         self.format = f
#
#
# class UnitValue(SetupTag):
#     def __init__(self, n, v= None, u = None):
#         super().__init__(n,v, u)
#         self.units = u
#

class SetupInformation:

    def __init__(self):
        #dictionary of dialog card names and their corresponding assignment functions
        #TODO make dynamic based on WizardTree names
        self.functionDictionary = {'Project Name':self.assignProjectName,
                                   'Data Input Format':self.assignDataFormat,
                                   'Load Wind Data':self.assignWindFolder,
                                   'Load Hydro Data':self.assignHydroFolder,
                                   'Raw Time Series':self.assignTimeseriesFolder,
                                   'Time Series Date Format':[self.assignDateChannel,SetupTag.assignFormat],
                                   'Input Interval':self.assignInputTimeStep,
                                   'Output Interval':self.assignOutputTimeStep
                                   }


        self.componentNames = ['wtg1P']
        self.headerNames = []

        self.inputDir = ''
        self.attributes = []
        self.units = []
        self.dateChannel = SetupTag('dateChannel')
        self.timeChannel = SetupTag('timeChannel')
        self.realLoadChannel = SetupTag('realLoadChannel')
        self.inputFileFormat = SetupTag('inputFileFormat')
        self.inputFileType = SetupTag('inputFileType')
        self.inputTimeStep = SetupTag('inputTimeStep')
        self.outputTimStep = SetupTag('outputTimeStep')
        self.inputFileDir = SetupTag('inputFileDir')


    #TODO currently each assignment just assigns a parameter, but this will likely change to perform some actions during parameter assigment. That is why each parameter has its own fuction
    def assignProjectName(self, name):
        import os
        self.projectName = name
        fileDir = os.getcwd()

        self.setupFolder = os.path.join(fileDir,'../../GBSProjects',self.projectName, 'InputData/Setup')
        print(self.setupFolder)

    def assignHeaderNames(self,name):
        self.headerNames = name

    def assignDataFormat(self, name):
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
        print(dialog)
        #TODO this is coming in null for date combo
        print(value)
        #if the dialog has a subheading pass the subheading to a SetupTag function
        method = self.functionDictionary[dialog]
        if type(method) is list:

            method[0](method[1],value)
        else:

            method(value)

    #creates a dictionary designed to feed into fillProjectData
    #->dictionary
    def getSetupTags(self):
        # TODO get keys for subclasses to create xml tags
        # keys = ['dateChannel', 'timeChannel', 'realLoadChannel', 'inputFileFormat', 'inputFileType', 'inputTimeStep', 'outputTimeStep','inputFileDir']
        # d = {k: {} for k in keys}
        # # all these need to be in the setup.xml template
        # d['dateChannel']['value'] = self.dateChannel
        # d['dateChannel']['format'] = self.dateFormat
        # d['timeChannel']['value'] = self.timeChannel
        # d['timeChannel']['format'] = self.timeFormat
        # d['realLoadChannel']['value'] = self.realLoadChannel
        # d['realLoadChannel']['units'] = self.realLoadUnits
        # d['inputFileFormat']['value'] = self.fileFormat
        # d['inputFileType']['value'] = self.fileType
        # d['inputTimeStep']['value'] = self.inputTimestep
        # d['inputTimeStep']['units'] = self.inputTimestepUnits
        # d['outputTimeStep']['value'] = self.outputTimestep
        # d['outputTimeStep']['units'] = self.outputTimestepUnits
        # d['inputFileDir']['value'] = self.inputDir
        d = {}
        for a in self.__dict__.keys():

            v = self.__getattribute__(a)
            if type(v) == SetupTag:
                d[v.name]=v.getDict()

        print(d)
        return d

    #read setup xml and assign values to the model parameters
    def readXML(self):
        import os
        from inputHandlerToUI import inputHandlerToUI
        fileDir = os.getcwd()
        projectDir = os.path.join(fileDir, '../../GBSProjects', self.projectName)
        # tell the controller to tell the InputHandler to read the xml
        inputHandlerToUI(projectDir, self)

        return True
    #write a new setup xml file for this project
    def writeNewXML(self):
        from userInputToHandler import userInputToHandler
        #tell controller to tell InputHandler package to write input xmls
        userInputToHandler(self)
        return True