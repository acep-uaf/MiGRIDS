#Component, string -> BeautifulSoup
#makes either a blank template soup or filled soup from existing component descriptor file

def makeSoup(component, saveDir):
    import os
    from createComponentDescriptor import createComponentDescriptor
    from fillProjectComponentData import fillProjectComponentData
    from readComponentXML import readComponentXML


    file = os.path.join(saveDir, component.component_name + 'Descriptor.xml')
    #if exists build soup

    if not os.path.isfile(file):
        # create a new xml based on template
        createComponentDescriptor(component, saveDir)
        # fill it with the minimal data we have
    fillProjectComponentData(component, saveDir)

    mysoup = readComponentXML(component.type, file)

    return mysoup