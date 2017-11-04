# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 2, 2017
# License: MIT License (see LICENSE file of this package for more information)

# initiates a project folder
def initiateProject(projectName,componentNames,saveDir):
    from buildComponentDescriptor import buildComponentDescriptor
    # initiate the component descriptor files and return a list of the names that correspond to an actual component
    componentNamesGood = buildComponentDescriptor(componentNames,saveDir)
    # initiate the setup file with the good component names
    from buildProjectSetup import buildProjectSetup
    buildProjectSetup(projectName,saveDir,componentNamesGood)