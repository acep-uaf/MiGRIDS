# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 31, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this accepts a list of component names with acceptable format and generates empty component descriptor files for them
# and saves them in the input directory specified. These files will then be updated each time the user updates the information
def buildComponentDescriptor(componentNames,saveDir):
    # General Imports
    from bs4 import BeautifulSoup
    import os

    # TODO: acceptable varnames can be populated from the names of component descriptor files instead of hard coded here
    varnames = ['gen','wtg','cl','controlledload','ees','tes','inv'] # acceptable names

    # cd to where component descriptors are located
    here = os.path.dirname(os.path.realpath(__file__))
    componentPath = os.path.join(here, '../GBSModel/Resources/Components')
    os.chdir(componentPath)

    for i in range(len(componentNames)):
        try:
            #ind = varnames.index(componentNames[i].lower())
            #ind = [varnames.index(i) for i in varnames if componentNames[i].lower() in i ]
            ind = [i for i, s in enumerate(varnames) if componentNames[i].lower() in s] # get the index of varnmaes that matches the input componentName

        except:
            print('Component name '+componentNames[i]+' is not valid.')
            print('Please use one of the following (case insensitive) as a prefix: ')
            print('%s' % ', '.join(map(str, varnames)))
            break



        fileName = varnames(ind)+'ComponentDescriptor.xml'
        infile_child = open(fileName, "r")
        contents_child = infile_child.read()
        infile_interface = open(fileName, 'r')
        contents_interface = infile_interface.read()

        soup = BeautifulSoup(contents_child, 'xml')
        titles = soup.find_all('title')
        for title in titles:
            print(title.get_text())

