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
        self.componentNames = ['wtg1P']
    #TODO currently each assignment just assigns a parameter, but this will likely change to perform some actions during parameter assigment. That is why each parameter has its own fuction
    def assignProjectName(self, name):
        import os
        self.projectName = name
        fileDir = os.getcwd()

        self.setupFolder = os.path.join(fileDir,'../../GBSProjects',self.projectName)
        print(self.setupFolder)

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
    #edit a tag attribute in the setup xml file
    def editXML(self):
        #edit
        #find the tags
        #edit the values

        return True
    #write a new setup xml file for this project
    def writeNewXML(self):
        from userInputToHandler import userInputToHandler
        #tell controller to tell InputHandler package to write input xmls
        userInputToHandler(self)
        return True