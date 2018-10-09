# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 8, 2018
# License: MIT License (see LICENSE file of this package for more information)
#This builds a project setup xml file
def copyProjectSetupFiles(projectName,componentNames,saveDir):
    '''This copies project setup files to the location of a new project.
    :param projectName: [string] the name of the project
    :param saveDir [string] is where the generated setup file will be saved'''

    # General Imports
    from bs4 import BeautifulSoup
    import os
    import glob

    if saveDir != '':
        # cd to where component descriptors are located
        here = os.path.dirname(os.path.realpath(__file__))
        setupPath = os.path.join(here, *['..','Model','Resources','Setup'])
        os.chdir(setupPath)
        fileNames = glob.glob("*.xml") # all xml files
        fileNames.remove('projectSetAttributes.xml') # this does not get copied
        for fileName in fileNames:
            os.chdir(setupPath)
            infile_child = open(fileName, "r")  # open
            contents_child = infile_child.read()
            infile_child.close()
            soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
            # update the project name and components if it is the Setup file
            if fileName == 'projectSetup.xml':
                soup.project.attrs['name'] = projectName
                soup.project.componentNames['value'] = componentNames
            #if the specified directory doesn't exist create it.
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
            os.chdir(saveDir)
            saveName = fileName.replace('project',projectName)
            f = open(saveName, "w")
            f.write(soup.prettify())
            f.close()
    return
