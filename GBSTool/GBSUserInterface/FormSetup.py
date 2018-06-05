
from PyQt5 import QtCore, QtWidgets

from GBSUserInterface.SetupWizard import SetupWizard
from GBSUserInterface.WizardTree import WizardTree
from GBSUserInterface.ModelSetupInformation import ModelSetupInformation
from GBSInputHandler.Component import Component
from GBSController.UIToHandler import UIToHandler
from GBSUserInterface.makeButtonBlock import makeButtonBlock
from GBSUserInterface.ResultsSetup import  ResultsSetup
from GBSUserInterface.FormModelRuns import SetsTableBlock
from GBSUserInterface.Pages import Pages
from GBSUserInterface.FileBlock import FileBlock
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from GBSUserInterface.loadSets import loadSets


class FormSetup(QtWidgets.QWidget):
    global model
    model = ModelSetupInformation()
    def __init__(self, parent):
        super().__init__(parent)
        
        self.initUI()
    #initialize the form
    def initUI(self):

        self.setObjectName("setupDialog")

        self.model = model

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()

        # the top block is buttons to load setup xml and data files
        self.createButtonBlock()
        windowLayout.addWidget(self.ButtonBlock)
        self.tabs = Pages(self, 'input1',FileBlock)
        #each file type gets its own page to specify formats and headers to include
        # button to create a new set tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Input')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)
        windowLayout.addWidget(newTabButton)

        windowLayout.addWidget(self.tabs,3)

        #list of dictionaries containing information for wizard
        #TODO move to seperate file
        dlist = [
            [{'title': 'Time Series Data', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'inputFileDirvalue', 'folder': True}, 'Data Input Format'],

            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'hydroFileDirvalue', 'folder': True}, 'Data Input Format'],

            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'windFileDirvalue', 'folder': True}, 'Data Input Format'],

            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_data_format', 'name': 'inputFileFormatvalue', 'folder': False},
             'Project'],

            [{'title': 'Project', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'project', 'folder': False}, None, ]

        ]

        self.WizardTree = self.buildWizardTree(dlist)
        button = QtWidgets.QPushButton('Create input files')
        button.setToolTip('Create input files to run models')
        button.clicked.connect(lambda: self.onClick(self.createInputFiles))
        button.setFixedWidth(200)
        #windowLayout.addWidget(makeButtonBlock(self,self.createInputFiles,'Create input files',None,'Create input files to run models'),3)
        windowLayout.addWidget(button)
        #set the main layout as the layout for the window

        self.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Setup')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #show the form
        self.showMaximized()



    #FormSetup -> QWidgets.QHBoxLayout
    #creates a horizontal button layout to insert in FormSetup
    def createButtonBlock(self):
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        #layout object name
        hlayout.setObjectName('buttonLayout')
        #add the button to load a setup xml

        hlayout.addWidget(makeButtonBlock(self, self.functionForLoadButton,
                                 'Load Existing Project', None, 'Load a previously created project files.'))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            makeButtonBlock(self,self.functionForCreateButton,
                                 'Create setup XML', None, 'Start the setup wizard to create a new setup file'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)
        hlayout.addStretch(1)
        self.ButtonBlock.setLayout(hlayout)

        self.ButtonBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        #self.ButtonBlock.setMinimumSize(self.size().width(),self.minimumSize().height())
        return hlayout

    #method -> None
    #calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self,buttonFunction):
        buttonFunction()

    #FormSetup -> None
    #method to modify FormSetup content
    def functionForCreateButton(self):

        #make a database
        #s is the 1st dialog box for the setup wizard

        s = SetupWizard(self.WizardTree, model, self)


        #display collected data
        hasSetup = model.feedSetupInfo()

        self.projectDatabase = False
        if hasSetup:
            self.fillData(model)
            self.topBlock.setEnabled(True)
            self.environmentBlock.setEnabled(True)
            self.componentBlock.setEnabled(True)
            #enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget,'pages')
            pages.enableTabs()

    #searches for and loads existing project data - database, setupxml,descriptors, DataClass pickle
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''
        import os
        from GBSUserInterface.replaceDefaultDatabase import replaceDefaultDatabase

        if (self.model.project == '') | (self.model.project is None):
            #launch file navigator to identify setup file
            setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", None, "*xml" )
            if (setupFile == ('','')) | (setupFile is None):
                return
            model.assignSetupFolder(setupFile[0])

            #Look for an existing component database and replace the default one with it
            if os.path.exists(os.path.join(self.model.projectFolder,'project_manager')):
                print('An existing project database was found for %s.' %self.model.project)

                replaceDefaultDatabase(os.path.join(self.model.projectFolder, 'project_manager'))
                self.projectDatabase = True
            else:
                self.projectDatabase = False
                print('An existing project database was not found for %s.' % self.model.project)

            # assign setup information to data model
            model.feedSetupInfo()
            # TODO this needs to be moved to a page block
            # display data
            #self.fillData(model)

            # look for an existing data pickle
            handler = UIToHandler()
            #TODO uncomment to load data
            #self.model.data = handler.loadInputData(os.path.join(self.model.setupFolder, self.model.project + 'Setup.xml'))
            if self.model.data is not None:
                self.updateModelPage(self.model.data)

                #refresh the plot
                resultDisplay = self.parent().findChild(ResultsSetup)
                resultDisplay.defaultPlot(self.model.data)
           # TODO uncomment
            # return true if sets have been run
            #setsRun = loadSets(model,self.window())
            setsRun = False

            #make the data blocks editable if there are no sets already created
            #if sets have been created then input data is not editable from the interface
            if setsRun:
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Analysis in Progress",
                                            "Analysis results were detected. You cannot edit projected input data after analysis has begun.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()
            else:
                self.tabs.setEnabled(True)

                print('Loaded %s:' % model.project)


        else:
            #TODO allow new projects to be loaded without closing window
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Close project", "You need to close the sofware before you load a new project")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
        return

    #TODO make dynamic from list input
    #List -> WizardTree
    def buildWizardTree(self, dlist):

        w1 = WizardTree(dlist[0][0], dlist[0][1], 2, [])
        #w2 = WizardTree(dlist[1][0], dlist[1][1], 1, [])  # hydro
        w3 = WizardTree(dlist[2][0], dlist[2][1], 0, [])  # wind
        w4 = WizardTree(dlist[3][0], dlist[3][1], 0, [w1, w3])  # inputFileFormat
        w5 = WizardTree(dlist[4][0], dlist[4][1], 0, [w4])
        return w5

    # send input data to the ModelSetupInformation data model
    # reads through all the file tabs to collect input
    # None->None
    def sendSetupData(self):

        headerName = []
        componentName = []
        componentAttribute = []
        componentAttributeU = []
        fileType = []
        dateChannel = []
        dateFormat = []
        timeChannel = []
        timeFormat = []
        fileDirectory= []
        # list of distinct components
        self.model.components = []
        #needs to come from each page

        tabWidget = self.findChild(QtWidgets.QTabWidget)
        for t in range(tabWidget.count):
            page = tabWidget.widget(t)
            # cycle through the input children in the topblock
            for child in self.topBlock.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox)):

                if type(child) is QtWidgets.QLineEdit:
                    value = child.text()

                else:
                    value = child.itemText(child.currentIndex())
                #append to appropriate list
                listx = globals(child.objectName())
                listx.append(value)

        # we also need headerNames, componentNames, attributes and units from the component section
            componentView = page.findChild((QtWidgets.QTableView), 'components')
            componentModel = componentView.model()
            for i in range(0, componentModel.rowCount()):
                headerName.append(componentModel.data(componentModel.index(i, 1)))
                componentName.append(componentModel.data(componentModel.index(i, 3)))
                componentAttribute.append(componentModel.data(componentModel.index(i, 7)))
                componentAttributeU.append(componentModel.data(componentModel.index(i, 4)))
                c = Component(component_name=componentModel.data(componentModel.index(i, 3)) + componentModel.data(
                    componentModel.index(i, 7)),
                              scale=componentModel.data(componentModel.index(i, 5)),
                              units=componentModel.data(componentModel.index(i, 4)),
                              offset=componentModel.data(componentModel.index(i, 6)),
                              attribute=componentModel.data(componentModel.index(i, 7)),
                              type=componentModel.data(componentModel.index(i, 2)),
                              original_field_name=componentModel.data(componentModel.index(i, 2)))
                self.model.components.append(c)
            # make a list of distinct values
            componentNames = list(set(componentName))
            # and the same data from the environment section
            envView = self.findChild((QtWidgets.QTableView), 'environment')
            envModel = envView.model()
            for j in range(0, envModel.rowCount()):
                headerName.append(envModel.data(envModel.index(j, 1)))
                componentName.append(envModel.data(envModel.index(j, 2)))
                componentAttribute.append(envModel.data(envModel.index(j, 6)))
                componentAttributeU.append(envModel.data(envModel.index(j, 3)))

                c = Component(component_name=envModel.data(envModel.index(j, 2)) + envModel.data(envModel.index(j, 6)),

                              scale=envModel.data(envModel.index(j, 4)),
                              units=envModel.data(envModel.index(j, 3)),
                              offset=envModel.data(envModel.index(j, 5)),
                              attribute=envModel.data(envModel.index(j, 6)),
                              original_field_name=envModel.data(envModel.index(j, 1)))
                self.model.components.append(c)
        model.assign('headerNamevalue', headerName)
        model.assign('componentNamevalue', componentName)
        model.assign('componentAttributevalue', componentAttribute)
        model.assign('componentAttributeunit', componentAttributeU)
        model.assign('componentNamesvalue', componentNames)
        model.assign('inputFileType', fileType)
        model.assign('inputFileDir',fileDirectory)
        model.assign('dateChannelvalue', dateChannel)
        model.assign('dateChannelformat',dateFormat)
        model.assign('timeChannelvalue',timeChannel)
        model.assign('timeChannelformat',timeFormat)

    # write data to the ModelSetupInformation data model and generate input xml files for setup and components
    # None->None
    def createInputFiles(self):
        import os
        self.addProgressBar()
        self.progress.setRange(0, 0)
        self.sendSetupData()
        # write all the xml files

        # start with the setupxml
        self.model.writeNewXML()

        # import datafiles
        handler = UIToHandler()
        cleaned_data, componentDict = handler.loadFixData(
            os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.updateModelPage(cleaned_data)
        # pickled data to be used later if needed
        handler.storeData(cleaned_data, os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.progress.setRange(0, 1)
        # generate netcdf files
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Time Series loaded",
                                    "Do you want to generate netcdf files?.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        result = msg.exec()
        # if yes create netcdf files, Otherwise this can be done after the data is reviewed.
        if result == QtWidgets.QMessageBox.Ok:
            handler.createNetCDF(cleaned_data.fixed, componentDict,
                                 os.path.join(model.setupFolder, model.project + 'Setup.xml'))

        return

    # DataClass with data frame called 'fixed' and field 'datetime'
    # updates default component list, time range and time step values in the setup table and passes these values to the modelDialog
    # DataClass -> None
    def updateModelPage(self, data):
        # start and end dates get set written to database as default date ranges
        import pandas as pd
        defaultStart = str((pd.to_datetime(data.fixed.index, unit='s')[0]).date())
        defaultEnd = str((pd.to_datetime(data.fixed.index, unit='s')[len(data.fixed.index) - 1]).date())

        defaultComponents = ','.join(self.model.componentNames.value)
        sqlHandler = ProjectSQLiteHandler()
        sqlHandler.cursor.execute(
            "UPDATE setup set date_start = ?, date_end = ?, component_names = ? where set_name = 'default'",
            [defaultStart, defaultEnd, defaultComponents])
        sqlHandler.connection.commit()
        sqlHandler.closeDatabase()
        # tell the model form to fillSetInfo now that there is data
        modelForm = self.window().findChild(SetsTableBlock)
        # start and end are tuples at this point
        modelForm.makeSetInfo(start=defaultStart, end=defaultEnd, components=defaultComponents)

    #event triggered when user navigates away from setup page
    #xml data gets written and the ModelSetupInformation attributes get updated
    #Event -> None
    def leaveEvent(self, event):
        # save xmls
        if 'projectFolder' in self.model.__dict__.keys():
            # on leave save the xml files
            # TODO uncomment
            #self.sendSetupData()
            #self.model.writeNewXML()
            return

    # close event is triggered when the form is closed
    def closeEvent(self, event):
        #save xmls
        if 'projectFolder' in self.model.__dict__.keys():
            # on close save the xml files
            self.sendSetupData()
            self.model.writeNewXML()
#TODO add progress bar for uploading raw data and generating fixed data pickle
    def addProgressBar(self):
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setObjectName('uploadBar')
        self.progress.setGeometry(100,100,100,50)
        return self.progress

    # add a new file input tab
    def newTab(self):
        # get the set count
        tab_count = self.tabs.count() +1
        widg = FileBlock(self, 'Input' + str(tab_count))
        #widg.fillSetInfo()
        self.tabs.addTab(widg, 'Input' + str(tab_count))

    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()


