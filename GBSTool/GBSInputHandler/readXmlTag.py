# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 21, 2017
# License: MIT License (see LICENSE file of this package for more information)

# read a value from an xml tag
def readXmlTag(fileName,tag,attr,fileDir=''):
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
    tagValues = a[attr].split( ) # if a list was written to an attribute, this will be read as a string, which needs to be parsed using spaces.
    return tagValues



