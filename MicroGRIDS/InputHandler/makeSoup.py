#string, string -> BeautifulSoup
#
def makeComponentSoup(component, saveDir):
    '''
    makes either a blank template soup or filled soup from existing component descriptor file
    assumes the component type is the first three characters of the component string.
    :param component: [String] the name of a component.
    :param saveDir: [String] the directory  to save to.
    :return: BeautifulSoup
    '''
    import os
    from InputHandler.createComponentDescriptor import createComponentDescriptor
    from UserInterface.readComponentXML import readComponentXML


    file = os.path.join(saveDir, component + 'Descriptor.xml')
    #if exists build soup
    if not os.path.isfile(file):
        # create a new xml based on template
        createComponentDescriptor(component, saveDir)

    componentType = component[0:3]
    mysoup = readComponentXML(componentType, file)

    return mysoup