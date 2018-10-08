def findDataDateLimits(setupXML):
    '''reads the runTimeSteps value in the setup xml and returns the value string
    :param setupXML:
    :return: [string] string value of multiple space sepearted dates
    '''

    from bs4 import BeautifulSoup
    # read the setupfile
    infile = open(setupXML, "r")
    contents = infile.read()

    soup = BeautifulSoup(contents, 'xml')
    rawIndices = None
    # get runTimeSteps child
    children = soup.findChildren()  # get all children
    target = children.find(name='runTimeSteps')
    rawIndices = target.value

    #close the xml
    infile.close()

    return processDates(rawIndices)

def processDates(rawIndices):
    if rawIndices is None:
        return None
    elif rawIndices == 'all':
        return None
    else:
        return rawIndices.split()