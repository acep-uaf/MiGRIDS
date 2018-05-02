#uses a set name and data model of component attribute changes to generate set#attribute.xml based on template
#string, Table -> Beautifulsoup
def makeAttributeXML(currentSet,model):
    from ProjectSQLiteHandler import ProjectSQLiteHandler
    soup = readAttributeXML()
    #update the soup to reflect the model
    #for each row in model
    compName =''
    compTag = ''
    compAttr=''
    compValue=''
    for i in range(model.rowCount()):
        compName = ' '.join([compName, model.data(i,2)])
        compTag = ' '.join([compTag, model.data(i,3).split('.')[:-1]])
        compAttr =  ' '.join([compAttr, model.data(i,3).split('.')[-1]])
        compValue = ' '.join([compValue, model.data(i, 4)])
    soup.compName.value = compName
    soup.compTag.value = compTag
    soup.compAttr.value = compAttr
    soup.compValue.value = compValue
    #update the set information
    handler = ProjectSQLiteHandler()
    dataTuple = handler.cursor.execute("SELECT set_name, date_start, date_end, timestep, component_names from setup where set_name = ?",currentSet.lower())
    soup.setupTag.value = "componentNames runTimeSteps timeStep"

    soup.setupAttr.value = "value value value"

    soup.setupValue.value = " ".join(dataTuple[4],timeStepsToInteger(dataTuple,[1],dataTuple[2]),dataTuple[3])

    return soup
def writeAttributeXML(soup,saveDir,setName):
    import os
    # write combined xml file
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    f = open(os.path.join(saveDir,setName), "w")
    f.write(soup.prettify())
    f.close()


#TODO create function to change dates into integer ranges for data input rows
def timeStepsToInteger(d1,d2,df):
    return 'all'


def readAttributeXML():
    from bs4 import BeautifulSoup
    import os
    # xml templates are in the model/resources/descriptor folder
    here = os.path.dirname(os.path.realpath(__file__))
    # pull xml from project folder
    resourcePath = os.path.join(here, '../GBSModel/Resources/Setup')
    # get list of component prefixes that correspond to componentDescriptors

    # read the xml file

    infile_child = open(os.path.join(resourcePath, 'projectSetAttributes.xml'), "r")  # open
    contents_child = infile_child.read()
    infile_child.close()
    soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
    parent = soup.childOf.string  # find the name of parent. if 'self', no parent file

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

    return soup