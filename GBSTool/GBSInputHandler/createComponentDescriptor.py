#
# build an empty descriptor file for a single component
#fill the descriptor file if a soup object is provided
#String string, Soup-> None
def createComponentDescriptor(component, saveDir, soup = None):
    # componentNames is a list of all components to be included in the simulation
    # saveDir is where the generated component descriptor files will be saved
    #this assumes that the first three characters in a component string is the component type

    # General Imports
    from bs4 import BeautifulSoup
    import os
    import re

    #get the component descriptor template from the resource folder
    #component descriptor can have parent files that contain additional tags
    here = os.path.dirname(os.path.realpath(__file__))
    componentPath = os.path.join(here, '../GBSModel/Resources/Components')

    def typeOfComponent(c):
        '''extracts the type of a component from its name
        :param c [String] the component name which consists of a component type + number'''
        match = re.match(r"([a-z]+)([0-9]+)", c, re.I)
        if match:
            componentType = match.group(1)
            return componentType
        return

    if soup is None:
        fileName = os.path.join(componentPath, typeOfComponent(component)+ 'Descriptor.xml')
        with open(fileName, "r") as template:# open
            print('creating from template')
            contents_child = template.read()
            template.close()
            soup = BeautifulSoup(contents_child, 'xml') # turn into soup
            parent = soup.childOf.string  # find the anme of parent. if 'self', no parent file
            parent = os.path.join(componentPath, parent)
            # update the component name
            soup.component.attrs['name'] = component
            while parent != 'self':  # continue to iterate if there are parents
                fileName = parent + '.xml'
                infile_child = open(fileName, "r")
                contents_child = infile_child.read()
                infile_child.close()
                soup2 = BeautifulSoup(contents_child, 'xml')
                # find parent. if 'self' then no parent
                parent = soup2.childOf.string

                for child in soup2.component.findChildren():  # for each tag under component
                    # check to see if this is already a tag. If it is, it is a more specific implementation, so don't add
                    # from parent file
                    if soup.component.find(child.name) is None:
                        soup.component.append(child)
        saveName = os.path.join(saveDir, component + 'Descriptor.xml')
    else:

        soup = soup
        saveName = os.path.join(saveDir, component + 'Descriptor.xml')
    # write combined xml file
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    f = open(saveName, "w")
    f.write(soup.prettify())
    f.close()

    return saveName