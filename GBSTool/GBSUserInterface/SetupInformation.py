'''SetupInformation is a data model for storing setup information collected through the SetupWizard or UISetupForm.
The information is written to an XML file using the writeXML method. '''

class SetupInformation:
    def __init__(self):
        #dictionary of dialog card names and their corresponding assignment functions
        #TODO make dynamic based on WizardTree names
        self.functionDictionary = {'Project Name':self.assignProjectName,
                                   'Data Input Format':self.assignDataFormat,
                                   'Load Wind Data':self.assignWindFolder,
                                   'Load Hydro Data':self.assignHydroFolder,
                                   'Raw Time Series':self.assignTimeseriesFolder,
                                   'Time Series Date Format':self.assignDateFormat,
                                   'Input Interval':self.assignInputInterval,
                                   'Output Interval':self.assignOutputInterval
                                   }
    #TODO currently each assignment just assigns a parameter, but this will likely change to perform some actions during parameter assigment. That is why each parameter has its own fuction
    def assignProjectName(self, name):
        self.projectName = name

    def assignDataFormat(self, name):
        self.dataFormat = name

    def assignInputInterval(self, name):
        self.InputInterval = name

    def assignOutputInterval(self, name):
        self.OutputInterval = name

    def assignWindFolder(self, name):
        self.WindFolder = name

    def assignHydroFolder(self, name):
        self.HydroFolder = name

    def assignTimeseriesFolder(self, name):
        self.TimeSeriesFolder = name

    def assignDateFormat(self, name):
        self.DateFormat= name


    def assign(self, dialog, value):
        method = self.functionDictionary[dialog]
        method(value)


    def writeXML(self):
        #write the information to a setup xml
        return True