
from PyQt5 import QtCore, QtWidgets, QtGui
import os

from GBSUserInterface.ModelSetupInformation import ModelSetupInformation
from GBSInputHandler.Component import Component
from GBSController.UIToHandler import UIToHandler
from GBSUserInterface.makeButtonBlock import makeButtonBlock
from GBSUserInterface.ResultsSetup import  ResultsSetup
from GBSUserInterface.FormModelRuns import SetsTableBlock
from GBSUserInterface.Pages import Pages
from GBSUserInterface.Delegates import ClickableLineEdit
from GBSUserInterface.FileBlock import FileBlock
from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from GBSUserInterface.ModelSetupInformation import SetupTag
from GBSUserInterface.switchProject import switchProject, saveProject, clearProjectDatabase

class FormSetup(QtWidgets.QWidget):
    global model
    model = ModelSetupInformation()
    def __init__(self, parent):
        super().__init__(parent)
        self.lastProjectPath = parent.lastProjectPath
        self.initUI()
    #initialize the form
    def initUI(self):
        self.dbHandler = ProjectSQLiteHandler()
        self.setObjectName("setupDialog")

        self.model = model

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()

        # the top block is buttons to load setup xml and data files
        self.createButtonBlock()
        windowLayout.addWidget(self.ButtonBlock)
        self.tabs = Pages(self, '1',FileBlock)
        self.tabs.setDisabled(True)
        #each file type gets its own page to specify formats and headers to include
        # button to create a new set tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Input')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)
        windowLayout.addWidget(newTabButton)

        windowLayout.addWidget(self.tabs,3)

        #list of dictionaries containing information for wizard
        #this is the information that is not input file specific.

        dlist = [
            {'title': 'Dates to model', 'prompt': 'Enter the timespan you would like to include in the model.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'runTimesteps', 'folder': False, 'dates':True},
            {'title': 'Timestep', 'prompt': 'Enter desired timestep', 'sqltable': None, 'sqlfield': None,
              'reftable': 'ref_time_units', 'name': 'timestep', 'folder': False},
            {'title': 'Project', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'project', 'folder': False}
        ]

        self.WizardTree = self.buildWizardTree(dlist)
        self.createBottomButtonBlock()
        windowLayout.addWidget(self.BottomButtons)
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

        self.ButtonBlock.setLayout(hlayout)

        self.ButtonBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        projectTitlewdg = QtWidgets.QLabel()
        projectTitlewdg.setObjectName('projectTitle')
        hlayout.addWidget(projectTitlewdg)
        hlayout.addStretch(1)
        return hlayout

        # FormSetup -> QWidgets.QHBoxLayout
        # creates a horizontal button layout to insert in FormSetup
    def createBottomButtonBlock(self):
        self.BottomButtons = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        # layout object name
        hlayout.setObjectName('buttonLayout')
        # add the button to load a setup xml
        button = QtWidgets.QPushButton('Create input files')
        button.setToolTip('Create input files to run models')
        button.clicked.connect(lambda: self.onClick(self.createInputFiles))
        button.setFixedWidth(200)
        # windowLayout.addWidget(makeButtonBlock(self,self.createInputFiles,'Create input files',None,'Create input files to run models'),3)
        hlayout.addWidget(button)
        dataLoaded = QtWidgets.QLineEdit()
        dataLoaded.setFrame(False)
        dataLoaded.setObjectName('dataloaded')
        dataLoaded.setText('No data loaded')
        dataLoaded.setFixedWidth(200)
        self.dataLoaded = dataLoaded
        hlayout.addWidget(self.dataLoaded)
        # generate netcd button
        netCDFButton = self.createSubmitButton()
        hlayout.addWidget(netCDFButton)
        button.setFixedWidth(200)
        self.netCDFsLoaded  = QtWidgets.QLineEdit()
        self.netCDFsLoaded.setFrame(False)
        self.netCDFsLoaded.setText("none")
        hlayout.addWidget(self.netCDFsLoaded)
        #hlayout.addStretch(1)
        self.BottomButtons.setLayout(hlayout)

        return hlayout

    #method -> None
    #calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self,buttonFunction):
        buttonFunction()

    #FormSetup -> None
    #method to modify FormSetup content
    def functionForCreateButton(self):
        #if a project is already started save it before starting a new one
        if (self.model.project != '') & (self.model.project is not None):
            self.model = switchProject(self)
            global model
            model = self.model

        s = self.WizardTree
        s.exec_()
        handler = UIToHandler()
        handler.makeSetup(model)
        #display collected data
        #returns true if setup info has been entered
        hasSetup = model.feedSetupInfo()
        self.projectDatabase = False
        if hasSetup:
            #self.topBlock.setEnabled(True)
            #self.environmentBlock.setEnabled(True)
            #self.componentBlock.setEnabled(True)
            #enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget,'pages')
            pages.enableTabs()
            self.tabs.setEnabled(True)
            self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.model.project)

    #searches for and loads existing project data - database, setupxml,descriptors, DataClass pickle
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''
        import os
        from GBSUserInterface.replaceDefaultDatabase import replaceDefaultDatabase
        #if we were already working on a project its state gets saved and  new project is loaded
        if (self.model.project != '') & (self.model.project is not None):
            self.model = switchProject(self)
            global model
            model = self.model

        #launch file navigator to identify setup file

        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", self.lastProjectPath, "*xml" )
        if (setupFile == ('','')) | (setupFile is None):
            return
        model.assignSetupFolder(setupFile[0])
        self.dbHandler.insertRecord('project',['project_path'],[setupFile[0]])

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

        #now that setup data is set display it in the form
        self.displayModelData()

        # look for an existing data pickle
        handler = UIToHandler()

        self.model.data = handler.loadInputData(os.path.join(self.model.setupFolder, self.model.project + 'Setup.xml'))
        if self.model.data is not None:
            self.updateModelPage(self.model.data)
            self.dataLoaded.setText('data loaded')
            #refresh the plot
            resultDisplay = self.parent().findChild(ResultsSetup)
            resultDisplay.defaultPlot()
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
        self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.model.project)

        return

    def displayModelData(self):
        """creates a tab for each input directory specified the SetupModelInformation model inputFileDir attribute.
        Each tab contains a FileBlock object to interact with the data input
        Each FileBlock is filled with data specific to the input directory"""
        self.tabs.removeTab(0)
        #the number of directories listed in inputFileDir indicates how many tabs are required
        tab_count = len(self.model.inputFileDir.value)
        #if directories have been entered then replace the first tab and create a tab for each directory #TODO should remove all previous tabs
        if tab_count > 0:
            self.tabs.removeTab(0)
            for i in range(tab_count):
                self.newTab(i+1)
        else:
            self.newTab(1)
        return

    #List -> WizardTree
    def buildWizardTree(self, dlist):
        """builds a QWizard based on list of inputs"""
        wiztree = QtWidgets.QWizard()
        wiztree.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        wiztree.setWindowTitle("Setup")
        wiztree.addPage(WizardPage(dlist[2]))
        wiztree.addPage(TextWithDropDown(dlist[1]))
        wiztree.addPage(TwoDatesDialog(dlist[0]))
        btn = wiztree.button(QtWidgets.QWizard.FinishButton)
        btn.clicked.connect(self.saveInput)
        return wiztree

    #save the input in the wizard tree to the setup data model
    def saveInput(self):
        """save the input in the wizard tree to the ModelSetupInformation data model"""
        model = self.model
        model.assignProject(self.WizardTree.field('project'))
        model.assignTimeStep(SetupTag.assignValue, self.WizardTree.field('timestep'))
        model.assignRunTimesteps(SetupTag.assignValue, self.WizardTree.field('sdate') + ' ' + self.WizardTree.field('edate'))
        return


    def sendSetupData(self):
        """ send input data to the ModelSetupInformation data model
        reads through all the file tabs to collect input
        """

        # list of distinct components
        self.model.components = []

        #needs to come from each page
        tabWidget = self.findChild(QtWidgets.QTabWidget)
        for t in range(tabWidget.count()):
            page = tabWidget.widget(t)
            # cycle through the input children in the topblock
            for child in page.FileBlock.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox)):

                if type(child) is QtWidgets.QLineEdit:
                    value = child.text()
                elif type(child) is ClickableLineEdit:
                    value = child.text()
                elif type(child) is QtWidgets.QComboBox:
                    value = child.itemText(child.currentIndex())
                #append to appropriate list
                attr = child.objectName()
                model.assign(attr,value,position=int(page.input)-1)

            page.saveTables()
    #TODO this should be done on a seperate thread
    # Create a dataframe of input data based on importing files within each SetupModelInformation.inputFileDir
    # None->None
    def createInputFiles(self):
        import os
        self.addProgressBar()
        self.progress.setRange(0, 0)
        self.sendSetupData()
        # check all the required fields are filled
        dbhandler = ProjectSQLiteHandler()
        if not dbhandler.dataComplete():
            #if required fields are not filled in return to setup page.
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Required Fields",
                                        "Please fill in all required fields before generating input files.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
            dbhandler.closeDatabase()
            return

        dbhandler.closeDatabase()
        # write all the xml files

        # start with the setupxml
        self.model.writeNewXML()


        # import datafiles
        handler = UIToHandler()
        cleaned_data, components = handler.loadFixData(
            os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.updateModelPage(cleaned_data)
        # pickled data to be used later if needed
        handler.storeData(cleaned_data, os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        handler.storeComponents(components,os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.dataLoaded.setText('data loaded')
        self.progress.setRange(0, 1)
        # generate netcdf files
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Time Series loaded",
                                    "Do you want to generate netcdf files?.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        result = msg.exec()

        # if yes create netcdf files, Otherwise this can be done after the data is reviewed.
        if result == QtWidgets.QMessageBox.Ok:
            d = {}
            for c in components:
                d[c.column_name] = c.toDictionary()
            handler.createNetCDF(cleaned_data.fixed, d,
                                 os.path.join(model.setupFolder, model.project + 'Setup.xml'))

        return

    # DataClass with data frame called 'fixed' and field 'datetime'
    # updates default component list, time range and time step values in the setup table and passes these values to the modelDialog
    # DataClass -> None
    def updateModelPage(self, data):
        # start and end dates get set written to database as default date ranges
        import pandas as pd
        def getDefaults(listDf,defaultStart=pd.to_datetime("1/1/1900").date(), defaultEnd = pd.datetime.today().date()):
            if len(listDf) > 0:
                s = listDf[0].index[0].date()
                e = listDf[0].index[len(listDf[0])-1].date()

                if (s < defaultStart) & (e > defaultEnd):
                    return getDefaults(listDf[1:],s,e)
                elif s < defaultStart:
                    return getDefaults(listDf[1:],s,defaultEnd)
                elif e > defaultStart:
                    return getDefaults(listDf[1:], defaultStart, e)
            return str(defaultStart), str(defaultEnd)

        #default start is the first date there is record for
        defaultStart, defaultEnd = getDefaults(data.fixed)
        defaultComponents = ','.join(self.model.componentNames.value)

        #TODO this should be moved to the handler
        #TODO this should be moved to the handler
        self.dbHandler.cursor.execute(
            "UPDATE setup set date_start = ?, date_end = ?, component_names = ? where set_name = 'default'",
            [defaultStart, defaultEnd, defaultComponents])
        self.dbHandler.connection.commit()

        # Deliver appropriate info to the ModelForm
        modelForm = self.window().findChild(SetsTableBlock)
        # start and end are tuples at this point
        modelForm.makeSetInfo(start=defaultStart, end=defaultEnd, components=defaultComponents)

        #deliver the data to the ResultsSetup form so it can be plotted
        resultsForm = self.window().findChild(ResultsSetup)
        resultsForm.setPlotData(data)

    # close event is triggered when the form is closed
    def closeEvent(self, event):
        #save xmls
        if 'projectFolder' in self.model.__dict__.keys():
            self.sendSetupData()
            # on close save the xml files
            self.model.writeNewXML()
            self.dbHandler.closeDatabase
        #close the fileblocks
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i)
            page.close()
    #TODO add progress bar for uploading raw data and generating fixed data pickle
    def addProgressBar(self):
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setObjectName('uploadBar')
        self.progress.setGeometry(100,100,100,50)
        return self.progress

    # add a new file input tab
    def newTab(self,i=0):
        # get the set count
        tab_count = self.tabs.count() +1
        widg = FileBlock(self, tab_count)
        #widg.fillSetInfo()
        self.tabs.addTab(widg, 'Input' + str(tab_count))
        #if its not the default empty tab fill data into form slots
        if i>0:
            widg.fillData(self.model,i)
    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

# ->QPushButton
    def createSubmitButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Generate netCDF inputs")
        button.clicked.connect(self.generateNetcdf)
        return button

    #uses the current data object to generate input netcdfs
    def generateNetcdf(self):

        handler = UIToHandler()
        #df gets read in from TimeSeries processed data folder
        #component dictionary comes from setupXML's
        MainWindow = self.window()
        setupForm = MainWindow.findChild(QtWidgets.QWidget,'setupDialog')
        setupModel= setupForm.model
        if 'setupFolder' in setupModel.__dict__.keys():
            setupFile = os.path.join(setupModel.setupFolder, setupModel.project + 'Setup.xml')
            componentModel = setupForm.findChild(QtWidgets.QWidget,'components').model()
            #From the setup file read the location of the input pickle
            #by replacing the current pickle with the loaded one the user can manually edit the input and
            #  then return to working with the interface
            data = handler.loadInputData(setupFile)
            if data:
                df = data.fixed
                componentDict = {}
                if 'components' not in setupModel.__dict__.keys():
                    #generate components
                    setupForm.makeComponentList(componentModel)
                for c in setupModel.components:
                    componentDict[c.component_name] = c.toDictionary()
                #filesCreated is a list of netcdf files that were generated
                filesCreated = handler.createNetCDF(df, componentDict,setupFile)
                self.netCDFsLoaded.setText(', '.join(filesCreated))
            else:
                print("no data found")


#classes used for displaying wizard inputs
class WizardPage(QtWidgets.QWizardPage):
    def __init__(self, inputdict,**kwargs):
        super().__init__()
        self.first = kwargs.get('first')
        self.last = kwargs.get('last')
        self.initUI(inputdict)

    # initialize the form
    def initUI(self, inputdict):
        self.d = inputdict
        self.setTitle(inputdict['title'])
        self.input = self.setInput()

        self.input.setObjectName(inputdict['name'])
        self.label = QtWidgets.QLabel()
        self.label.setText(inputdict['prompt'])
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)
        n = inputdict['name']
        self.registerField(inputdict['name'],self.input)

        return

    def setInput(self):
        wid = QtWidgets.QLineEdit()
        return wid

    def getInput(self):
        return self.input.text()


class TwoDatesDialog(WizardPage):
    def __init__(self,d):
        super().__init__(d)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.startDate = QtWidgets.QDateEdit()
        self.startDate.setObjectName('start')
        self.startDate.setDisplayFormat('yyyy-MM-dd')
        self.startDate.setCalendarPopup(True)
        self.endDate = QtWidgets.QDateEdit()
        self.endDate.setObjectName('end')
        self.endDate.setDisplayFormat('yyyy-MM-dd')
        self.endDate.setCalendarPopup(True)
        box.addWidget(self.startDate)
        box.addWidget(self.endDate)
        grp.setLayout(box)
        name = self.d['name']
        self.registerField('sdate', self.startDate,"text")
        self.registerField('edate',self.endDate,"text")
        return grp

    def getInput(self):
        return " - ".join([self.startDate.text(),self.endDate.text()])

class DropDown(WizardPage):
    def __init__(self,d):
        super().__init__(d)

    def setInput(self):
        self.input = QtWidgets.QComboBox()
        self.input.setItems(self.getItems())
        return
    def getInput(self):
        return self.breakItems(self.input.itemText(self.input.currentIndex()))

    def getItems(self):

        items = self.dbHandler.getCodes(self.d['reftable'])
        return items
    def breakItems(self,str):
        item = str.split(' - ')[0]
        return item


class TextWithDropDown(WizardPage):
    def __init__(self, d):
        super().__init__(d)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.combo = QtWidgets.QComboBox()

        self.combo.addItems(self.getItems())
        self.text = QtWidgets.QLineEdit()
        self.text.setValidator(QtGui.QIntValidator())
        box.addWidget(self.text)
        box.addWidget(self.combo)
        grp.setLayout(box)
        #self.registerField(self.d['name'],self.combo,"currentText",self.combo.currentIndexChanged)
        self.registerField('timeInterval',self.text)
        self.registerField('timeUnit',self.combo,"currentText")
        return grp

    def getInput(self):
        input = self.text.text()
        item = self.breakItems(self.input.itemText(self.input.currentIndex()))
        strInput = ' '.join([input,item])
        return strInput
    def getItems(self):
        dbHandler = ProjectSQLiteHandler()
        items = dbHandler.getCodes(self.d['reftable'])
        dbHandler.closeDatabase()
        return items

    def breakItems(self, str):
        item = str.split(' - ')[0]
        return item