#string, string -> BeautifulSoup
#makes either a blank template soup or filled soup from existing component descriptor file
#assumes the component type is the first three characters of the component string
def makeSoup(component, saveDir):
    import os
    from createComponentDescriptor import createComponentDescriptor
    from readComponentXML import readComponentXML


    file = os.path.join(saveDir, component + 'Descriptor.xml')
    #if exists build soup
    if not os.path.isfile(file):
        # create a new xml based on template
        createComponentDescriptor(component, saveDir)

    componentType = component[0:3]
    mysoup = readComponentXML(componentType, file)

    return mysoup