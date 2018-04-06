# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 3, 2017
# License: MIT License (see LICENSE file of this package for more information)

# fill in information about the project into the descriptor and setup xml files
#Does not interact directly with User Interface but takes object containing relevent information passed
#from user interface through controller.
#if setupInfo is none then csv files are assumed
#String, SetupInformation - > None
def fillProjectData(projectDir = '',setupInfo = None):
    # general imports
    # add to sys path
    import sys
    import os
    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)
    import tkinter as tk
    from tkinter import filedialog
    from fillProjectDataFromCSV import fillProjectDataFromCSV
    from fillProjectDataFromUI  import fillProjectDataFromUI
    from fillProjectComponentData import fillProjectComponentData



    # get the project directory. This is all that should be needed, since folder structure and filenames should be
    # standardized
    # if project directory not specified, ask for it
    if projectDir == '':
        print('Choose the project directory')
        root = tk.Tk()
        root.withdraw()
        projectDir = filedialog.askdirectory()

    userInputDir = projectDir + '/InputData/Setup/UserInput/'

    if setupInfo is None:
        fillProjectDataFromCSV(userInputDir)

    else:
        fillProjectDataFromUI(projectDir,setupInfo)
        # get possible headers
        if setupInfo.possibleHeaders is not None:
            fillProjectComponentData(projectDir, setupInfo)