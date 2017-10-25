# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def readDataFile(inputSpecification,fileLocation='',fileType='csv',columnNames=None,useNames=None):
    # inputSpecification points to a script to accept data from a certain input data format
    # fileLocation is the dir where the data files are stored. It is either absolute or relative to the GBS project InputData dir
    # fileType is the file type. default is csv. All files of this type will be read from the dir
    # columnNames, if specified, is a list of column names from the data file that will be returned in the dataframe.
    # otherwise all columns will be returned. Note indexing starts from 0.

    import pandas as pd
    import os
    try:
        # try to see if the input file location is an absolute address
        os.chdir(fileLocation)
    except:
        # if it is not absolute, try to find it in the project folder
        dir = os.path.dirname(__file__)
        newdir = os.path.join(dir, '..\..\InputData', fileLocation)
        os.chdir(newdir)
        # get a list of all files.
    here = os.getcwd()
    fileNames = [f for f in os.listdir(here) if
                 os.path.isfile(f) & f.endswith(fileType)]  # get just the filenames ending with fileType

    # depending on input specification, different procedure
    if inputSpecification=='AVEC':
    # In the case of AVEC, data files are broken into months. Append them.
        from readAvecCsv import readAvecCsv

        for i in range(len(fileNames)): # for each data file
            if i == 0:
                df = readAvecCsv(fileNames[i],fileLocation,columnNames,useNames)  # read data file into a new dataframe if first iteration
            else:
                df.append(readAvecCsv(fileNames[i],fileLocation,columnNames,useNames)) # otherwise append


    return df

