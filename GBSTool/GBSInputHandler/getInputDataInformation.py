# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads information on how to process input data
def getInputDataInformation():

    # temporary fix

    #### get user to select the input file ####
    # this could be hard coded if they will always be located at the same point in the file tree.
    print('Choose directory where the input data files are located.')
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    #fileLocation = filedialog.askdirectory()
    fileName = filedialog.askopenfilename()

    from bs4 import BeautifulSoup
    infile_child = open(fileName, "r")
    contents_child = infile_child.read()
    infile_interface = open(fileName, 'r')
    contents_interface = infile_interface.read()

    soup = BeautifulSoup(contents_child, 'xml')
    titles = soup.find_all('title')
    for title in titles:
        print(title.get_text())

    # get project name
    projectName = soup.project.attrs['name']
    # find parent. if 'self' then no parent
    parent = soup.childOf.string.lower()
    # get children
    children = soup.findChildren() # get all children
    for i in range(len(children)):
        name = children[i].name
        attributes = children[i].attrs
        grandkids = children[i].findChildren





getInputDataInformation()
