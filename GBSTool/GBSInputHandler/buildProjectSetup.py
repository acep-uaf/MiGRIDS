# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 31, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this accepts a list of component names with acceptable format and generates empty component descriptor files for them
# and saves them in the input directory specified. These files will then be updated each time the user updates the information
def buildProjectSetup(projectName,saveDir,componentNames):
    # componentNames is a list of all components to be included in the simulation
    # saveDir is where the generated component descriptor files will be saved

    # General Imports
    from bs4 import BeautifulSoup
    import os

    if saveDir != '':
        # cd to where component descriptors are located
        here = os.path.dirname(os.path.realpath(__file__))
        setupPath = os.path.join(here, '../GBSModel/Resources/Setup')

        fileName = os.path.join(setupPath,'projectSetup.xml') # get filename
        infile_child = open(fileName, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
        # update the project name
        soup.project.attrs['name'] = projectName
        soup.project.componentNames['value'] = componentNames
        # save
        #if the specified directory doesn't exist create it.
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        else:
            return
        saveName = os.path.join(saveDir, projectName + 'Setup.xml')
        f = open(saveName, "w")
        f.write(soup.prettify())
        f.close()

