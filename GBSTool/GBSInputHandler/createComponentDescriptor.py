#build an empty descriptor file for a single component
#Component, string -> None
def createComponentDescriptor(component, saveDir):
    # componentNames is a list of all components to be included in the simulation
    # saveDir is where the generated component descriptor files will be saved

    # General Imports
    from bs4 import BeautifulSoup
    import os


    #get the component descriptor template from the resource folder
    #component descriptor can have parent files that contain additional tags
    here = os.path.dirname(os.path.realpath(__file__))
    componentPath = os.path.join(here, '../GBSModel/Resources/Components')
    print(component.component_name)
    print(component.type)
    fileName = os.path.join(componentPath, component.type +'Descriptor.xml')
    with open(fileName, "r") as template:# open
        contents_child = template.read()
        template.close()
        soup = BeautifulSoup(contents_child, 'xml') # turn into soup
        parent = soup.childOf.string  # find the anme of parent. if 'self', no parent file
        parent = os.path.join(componentPath, parent)
        # update the component name
        soup.component.attrs['name'] = component.component_name
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
        # write combined xml file
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        os.chdir(saveDir)
        saveName = component.component_name+'Descriptor.xml'
        f = open(saveName, "w")
        f.write(soup.prettify())
        f.close()

    return saveName