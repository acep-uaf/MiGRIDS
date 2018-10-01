def findDataDateLimits(setupXML):
    """reads the runTimeSteps value in the setup xml and returns the value string"""
    from bs4 import BeautifulSoup
    # read teh setupfile
    infile = open(setupXML, "r")
    contents = infile.read()

    soup = BeautifulSoup(contents, 'xml')
    rawIndices = None
    # get runTimeSteps child
    children = soup.findChildren()  # get all children
    # find all the children and assign them to the setupInfo model
    for i in range(len(children)):
        # the project tag is different so skip it here
        if children[i].name == 'runTimeSteps':
            rawIndices = children[i].value

    infile.close()

    return processDates(rawIndices)

def processDates(rawIndices):
    if rawIndices is None:
        return None
    elif rawIndices == 'all':
        return None
    else:
        return rawIndices.split()