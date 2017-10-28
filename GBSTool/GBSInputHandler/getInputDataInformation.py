# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 27, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads information on how to process input data
def getInputDataInformation():

    # temporary fix

    print('Choose directory where component descriptor files are located.')
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    fileLocation = filedialog.askdirectory()

    import os
    os.chdir(fileLocation)


    return ncfile

