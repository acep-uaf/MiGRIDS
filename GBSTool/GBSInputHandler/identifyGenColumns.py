# listOfComponents -> listOfComponents
# returns a list of components that are diesel generators (start with 'gen')
def identifyGenColumns(componentList):
    genColumns = []
    for c in componentList:
        if (c[:3].lower() == 'gen') & (c[-1].lower() == 'p'):
            genColumns.append(c)
    return genColumns