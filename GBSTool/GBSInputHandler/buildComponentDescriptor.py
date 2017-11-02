# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 31, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this accepts a list of component names with acceptable format and generates empty component descriptor files for them
# and saves them in the input directory specified. These files will then be updated each time the user updates the information
def buildComponentDescriptor(componentNames,saveDir):
    # componentNames is a list of all components to be included in the simulation
    # saveDir is where the generated component descriptor files will be saved

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
            ind = [j for j, s in enumerate(varnames) if s in componentNames[i].lower()]            # get the index of varnmaes that matches the input componentName

        except:
            print('Component name '+componentNames[i]+' is not valid.')
            print('Please use one of the following (case insensitive) as a prefix: ')
            print('%s' % ', '.join(map(str, varnames)))
            break
        else:
            # read the xml file
            fileName = varnames[ind[0]]+'Descriptor.xml' # get filename
            infile_child = open(fileName, "r") # open
            contents_child = infile_child.read()
            infile_child.close()
            soup = BeautifulSoup(contents_child, 'xml') # turn into soup
            parent = soup.childOf.string.lower() # find the anme of parent. if 'self', no parent file

            while parent != 'self': # continue to iterate if there are parents
                fileName = parent + '.xml'
                infile_child = open(fileName, "r")
                contents_child = infile_child.read()
                infile_child.close()
                soup2 = BeautifulSoup(contents_child, 'xml')
                # add new elements from soup2 into soup
                for element in soup2.body:
                    soup.body.append(element)
                # find parent. if 'self' then no parent
                parent = soup2.childOf.string

            # write combined xml file
            saveName = componentNames[i]+'Descriptor.xml'
            f = open(saveName, "w")
            f.write(soup.prettify())
            f.close()


buildComponentDescriptor(['gen1','gen2','wtg1'],'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools1\GBSProjects\Chevak\InputData\Components')