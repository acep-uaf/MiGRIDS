# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 3, 2017
# License: MIT License (see LICENSE file of this package for more information)

# fill in information about the project into the descriptor and setup xml files
def fillProjectData(fileDir):
    # general imports
    import tkinter as tk
    from tkinter import filedialog
    import pandas as pd

    # TODO: some sore of GUI to get data from user
    # for now get data from csv files
    # first get
    print('Choose the csv file where the component information is stored.')
    root = tk.Tk()
    root.withdraw()
    fileName = filedialog.askopenfile()
    df = pd.read_csv(fileName) # read as a data frame

    for row in range(df.shape[0]):
        fileName = df['componentName'][row]
        writeXmlTag(fileName,tag,attr,value,fileDir)

fillProjectData('C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools1\GBSProjects\Chevak\InputData\Setup')