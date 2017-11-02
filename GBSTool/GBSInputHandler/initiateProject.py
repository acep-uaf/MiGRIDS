# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 2, 2017
# License: MIT License (see LICENSE file of this package for more information)

# initiates a project folder
def initiateProject(projectName,componentNames,saveDir):
    from buildComponentDescriptor import buildComponentDescriptor

    buildComponentDescriptor(componentNames,saveDir)

    from buildProjectSetup import buildProjectSetup

    buildProjectSetup(projectName,saveDir)