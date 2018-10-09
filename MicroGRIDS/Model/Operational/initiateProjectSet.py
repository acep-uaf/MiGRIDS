# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 8, 2018
# License: MIT License (see LICENSE file of this package for more information)
import os

# initiates a project folder
def initiateSet(projectDir,setID):
    """
    Initiates the directory and the projectSetAttributes.xml file for a new set of simulations
    :param projectDir: [string] the name of the project or the path to the project directory that needs to be created
    :param setID: [string] the ID of the new set
    :return:
    """
    from bs4 import BeautifulSoup
    import os
    import glob

    # split into path and name
    projectDirBase, projectName = os.path.split(projectDir)
    if projectDirBase == '':
        here = os.path.dirname(os.path.realpath(__file__))
        projectDir = os.path.join(here,'..','..','..','MicroGRIDSProjects',projectName)
    # cd to setup files location
    here = os.path.dirname(os.path.realpath(__file__))
    setupPath = os.path.join(here, *['..','..', 'Model', 'Resources', 'Setup'])
    os.chdir(setupPath)
    infile_child = open('projectSetAttributes.xml', "r")  # open
    contents_child = infile_child.read()
    infile_child.close()
    soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
    soup.project.attrs['name'] = projectName
    soup.setNumber.attrs['value'] = setID
    setDir = os.path.join(projectDir,'OutputData','Set'+setID)
    if os.path.isdir(setDir):
        print('Set'+setID+' already exists in this project. Choose a different set ID.')
    else:
        # if does not already exist, create
        os.mkdir(setDir)
        os.chdir(setDir)
        saveName = projectName + 'SetAttributes.xml'
        f = open(saveName, "w")
        f.write(soup.prettify())
        f.close()


