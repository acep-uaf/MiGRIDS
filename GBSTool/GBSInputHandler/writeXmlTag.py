# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 2, 2017
# License: MIT License (see LICENSE file of this package for more information)

# write a value to an xml tag
def writeXmlTag(fileName,tagPath,value,fileDir):
    # general imports
    import os
    from bs4 import BeautifulSoup

    # cd to file location
    os.chdir(fileDir)

    # open file and read into soup
    infile_child = open(fileName, "r")  # open
    contents_child = infile_child.read()
    infile_child.close()
    soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

    for i in range(len(tagPath)-1): # each step in the path should be a tag until the last one, which should be an attribute
