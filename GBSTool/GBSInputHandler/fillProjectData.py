# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 3, 2017
# License: MIT License (see LICENSE file of this package for more information)

# fill in information about the project into the descriptor and setup xml files
#
#String, ModelSetupInformation - > None
def fillProjectData(projectDir = '',setupInfo = None):
    '''
    Calls function to create project data files depending on what parameters are provided
    Does not interact directly with User Interface but takes object containing relevent information passed
    from user interface through controller.If setupInfo is none then csv files are assumed
    :param projectDir: [string] the directory that project data is saved in
    :param setupInfo: [ModelSetupInformation] a model of setup information collected from the user interface
    :return: None
    '''
    # general imports
    import sys
    import os
    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)
    import tkinter as tk
    from tkinter import filedialog
    from GBSInputHandler.fillProjectDataFromCSV import fillProjectDataFromCSV
    from GBSInputHandler.fillProjectDataFromUI  import fillProjectDataFromUI

    # get the project directory. This is all that should be needed, since folder structure and filenames should be
    # standardized
    # if project directory not specified, ask for it
    if projectDir == '':
        print('Choose the project directory')
        root = tk.Tk()
        root.withdraw()
        projectDir = filedialog.askdirectory()

    if setupInfo is None:
        fillProjectDataFromCSV(projectDir)
    else:
        fillProjectDataFromUI(setupInfo)
    return