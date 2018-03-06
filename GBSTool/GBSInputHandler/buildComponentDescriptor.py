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

    # cd to where component descriptors are located
    here = os.path.dirname(os.path.realpath(__file__))
    componentPath = os.path.join(here, '../GBSModel/Resources/Components')
    os.chdir(componentPath)
    # get list of component prefixes that correspond to componentDescriptors
    varnames = []
    for file in os.listdir():
        if file.endswith("Descriptor.xml"):
            varnames.append(file[0:len(file)-14])
    # initiate var to store the good component names
    componentNamesGood = []
    for i in range(len(componentNames)):
        #ind = varnames.index(componentNames[i].lower())
        #ind = [varnames.index(i) for i in varnames if componentNames[i].lower() in i ]
        ind = [j for j, s in enumerate(varnames) if s in componentNames[i].lower()]            # get the index of varnmaes that matches the input componentName

        if len(ind)==0:
            print('Component name '+componentNames[i]+' is not valid.')
            print('Please use one of the following (case insensitive) as a prefix: ')
            print('%s' % ', '.join(map(str, varnames)))
        else:
            # read the xml file
            os.chdir(componentPath)
            fileName = varnames[ind[0]]+'Descriptor.xml' # get filename
            infile_child = open(fileName, "r") # open
            contents_child = infile_child.read()
            infile_child.close()
            soup = BeautifulSoup(contents_child, 'xml') # turn into soup
            parent = soup.childOf.string # find the anme of parent. if 'self', no parent file
            # update the component name
            soup.component.attrs['name'] = componentNames[i]
            componentNamesGood.append(componentNames[i])
            while parent != 'self': # continue to iterate if there are parents
                fileName = parent + '.xml'
                infile_child = open(fileName, "r")
                contents_child = infile_child.read()
                infile_child.close()
                soup2 = BeautifulSoup(contents_child, 'xml')
                # find parent. if 'self' then no parent
                parent = soup2.childOf.string

                for child in soup2.component.findChildren(): # for each tag under component
                    # check to see if this is already a tag. If it is, it is a more specific implementation, so don't add
                    # from parent file
                    if soup.component.find(child.name) is None:
                        soup.component.append(child)


            # write combined xml file
            os.chdir(saveDir)
            saveName = componentNames[i]+'Descriptor.xml'
            f = open(saveName, "w")
            f.write(soup.prettify())
            f.close()

    return componentNamesGood