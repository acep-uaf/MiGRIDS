# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 2, 2017
# License: MIT License (see LICENSE file of this package for more information)

# write a value to an xml tag
def writeXmlTag(fileName,tag,attr,value,fileDir=''):
    # general imports
    import os
    from bs4 import BeautifulSoup

    # cd to file location
    if fileDir != '':
        os.chdir(fileDir)

    # open file and read into soup
    infile_child = open(fileName, "r")  # open
    contents_child = infile_child.read()
    infile_child.close()
    soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

    # assign value
    if isinstance(tag,(list,tuple)): # if tag is a list or tuple, itereate down
        a = soup.find(tag[0])
        for i in range(1,len(tag)): # for each other level of tags, if there are any
            a = a.find(tag[i])
    else: # if it is just one string
        a = soup.find(tag)
    # convert value to strings if not already
    if isinstance(value, (list, tuple)): # if a list or tuple, iterate
        value = [str(e) for e in value]
    else:
        value = str(value)
    a[attr] = value


    # save again
    if fileDir != '':
        os.chdir(fileDir)
    f = open(fileName, "w")
    f.write(soup.prettify())
    f.close()


