#build an empty descriptor file for a single component
#Component, string -> None
def createComponentDescriptor(component, saveDir):
    # componentNames is a list of all components to be included in the simulation
    # saveDir is where the generated component descriptor files will be saved

    # General Imports
    from bs4 import BeautifulSoup
    import os


    #get the component descriptor template from the resource folder
    here = os.path.dirname(os.path.realpath(__file__))
    componentPath = os.path.join(here, '../GBSModel/Resources/Components')

    fileName = os.path.join(componentPath, component.type, 'Descriptor.xml')
    with open(fileName, "r") as template:# open
        contents_child = template.read()
        template.close()
        soup = BeautifulSoup(contents_child, 'xml') # turn into soup
        # update the component name
        soup.component.attrs['name'] = component.name

        # write combined xml file
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        os.chdir(saveDir)
        saveName = component.name+'Descriptor.xml'
        f = open(saveName, "w")
        f.write(soup.prettify())
        f.close()

    return