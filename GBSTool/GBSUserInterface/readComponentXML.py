def readComponentXML(componentType, infile = None):
    from bs4 import BeautifulSoup
    import os
    # xml templates are in the model/resources/descriptor folder
    here = os.path.dirname(os.path.realpath(__file__))
    # pull xml from project folder
    componentPath = os.path.join(here, '../GBSModel/Resources/Components')
    # get list of component prefixes that correspond to componentDescriptors

    # read the xml file
    #if there is no file, make one from the template
    #os.chdir(componentPath)
    if infile is None:
        fileName = os.path.join(componentPath, componentType + 'Descriptor.xml')  # get filename
        infile_child = open(fileName, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
        parent = soup.childOf.string  # find the anme of parent. if 'self', no parent file

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
    #if there is an existing file read it.
    else:

        infile_child = open(infile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')
    return soup