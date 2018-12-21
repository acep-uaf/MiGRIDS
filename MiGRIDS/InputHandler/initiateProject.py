# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 2, 2017
# License: MIT License (see LICENSE file of this package for more information)
import os

# initiates a project folder
def initiateProject(projectDir,componentNames):
    '''
    Calls buildProjectSetup to generate a project directory.
    :param projectDir: [String] the name of the project or the path to the project directory that needs to be created
    :param componentNames: [String] the names of components (space delimited)
    :return:
    '''
    from MiGRIDS.InputHandler.buildAllComponentDescriptor import buildComponentDescriptor
    from MiGRIDS.InputHandler.copyProjectSetupFiles import copyProjectSetupFiles
    # split into path and name
    projectDirBase, projectName = os.path.split(projectDir)
    if projectDirBase == '':
        here = os.path.dirname(os.path.realpath(__file__))
        projectDir = os.path.join(here,'..','..','MiGRIDSProjects',projectName)
    if os.path.isdir(projectDir):
        print("Project " + projectName + " already exists.")
    else:
        os.mkdir(projectDir)
        os.mkdir(os.path.join(projectDir,'OutputData'))
        os.mkdir(os.path.join(projectDir, 'InputData'))
        os.mkdir(os.path.join(projectDir, 'InputData','Components'))
        os.mkdir(os.path.join(projectDir, 'InputData', 'Setup'))
        os.mkdir(os.path.join(projectDir, 'InputData', 'TimeSeriesData'))
        os.mkdir(os.path.join(projectDir, 'InputData', 'TimeSeriesData','RawData'))
        os.mkdir(os.path.join(projectDir, 'InputData', 'TimeSeriesData', 'ProcessedData'))
        componentDir = os.path.join(projectDir, 'InputData','Components')
        setupDir = os.path.join(projectDir, 'InputData','Setup')

        # initiate the component descriptor files and return a list of the names that correspond to an actual component
        componentNamesGood = buildComponentDescriptor(componentNames, componentDir)
        # initiate the setup file with the good component names
        copyProjectSetupFiles(projectName,componentNamesGood,setupDir)

