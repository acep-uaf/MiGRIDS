# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 2, 2017
# License: MIT License (see LICENSE file of this package for more information)

# initiates a project folder
def initiateProject(projectName,componentNames,componentDir,setupDir):
    '''
    Calls buildProjectSetup to generate a project directory.
    :param projectName: [String] the name of the project.
    :param componentNames: [String] the names of components (space delimited)
    :param componentDir: [String] the pathto the project directory.
    :param setupDir: [String] the setufile path.
    :return:
    '''
    from GBSInputHandler.buildAllComponentDescriptor import buildComponentDescriptor
    from GBSInputHandler.buildProjectSetup import buildProjectSetup

    # initiate the component descriptor files and return a list of the names that correspond to an actual component
    componentNamesGood = buildComponentDescriptor(componentNames, componentDir)
    # initiate the setup file with the good component names

    buildProjectSetup(projectName,setupDir, None)