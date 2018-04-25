#String, SetupInformation ->
#modifies the ModelSetupInformation object based on tags in the setup xml
def getSetupInformation(setupXML, setupInfo):

    from bs4 import BeautifulSoup
    #read teh setupfile
    infile = open(setupXML, "r")
    contents = infile.read()
    setupInfo.getSetupTags()
    soup = BeautifulSoup(contents, 'xml')

    # # get project name
    setupInfo.project = soup.project.attrs['name']

    # get children
    children = soup.findChildren()  # get all children
    #find all the children and assign them to the setupInfo model
    for i in range(len(children)):
        #the project tag is different so skip it here
        if children[i].name != 'project':
            setupInfo.assign(children[i].name,children[i].name)

            if children[i].attrs is not None:
                for k in children[i].attrs.keys():

                    setupInfo.assign(children[i].name + k, children[i][k])

    infile.close()

