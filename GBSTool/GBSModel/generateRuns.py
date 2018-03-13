# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 12, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
from GBSInputHandler.readXmlTag import readXmlTag
import numpy as np
import pandas as pd
import itertools
import sqlite3

# TODO: this needs to be fixed
def generateRuns(projectSetDir):
    os.chdir(projectSetDir) # change directories to the directory for this set of simulations
    # get the set number
    dir_path = os.path.basename(projectSetDir)
    setNum = int(dir_path[3:])

    # load the file with the list of different component attributes
    compName = readXmlTag('set'+str(setNum) + 'ComponentAttributes.xml', ['compAttributeValues', 'compName'], 'value')
    compTag = readXmlTag('set' + str(setNum) + 'ComponentAttributes.xml', ['compAttributeValues', 'compTag'], 'value')
    compAttr = readXmlTag('set' + str(setNum) + 'ComponentAttributes.xml', ['compAttributeValues', 'compAttr'], 'value')
    compValue = readXmlTag('set' + str(setNum) + 'ComponentAttributes.xml', ['compAttributeValues', 'compValue'], 'value')

    # get unique list of components
    compNameUnique = np.unique(compName)

    valSplit = [] # list of lists of attribute values
    for val in compValue: # iterate through all comonent attributes
        valSplit.append(val.split(',')) # split according along commas

    # get all possible combinations of the attribute values
    runValues = list(itertools.product(*valSplit))

    # get headings
    heading = [x + compTag[idx] + '/' + compAttr[idx] for idx, x in enumerate(compName)]

    # create dataframe and save as SQL
    df = pd.DataFrame(data = runValues, columns = heading)
    conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db') # create sql database
    df.to_sql('compAttributes', conn) # write to table compAttributes in db
    conn.close()



