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
from GBSInputHandler.writeXmlTag import writeXmlTag
import numpy as np
import pandas as pd
import itertools
import sqlite3
from shutil import copyfile

# TODO: this needs to be fixed
def generateRuns(projectSetDir):
    os.chdir(projectSetDir) # change directories to the directory for this set of simulations
    # get the set number
    dir_path = os.path.basename(projectSetDir)
    setNum = int(dir_path[3:])
    # get the project name
    os.chdir(projectSetDir)
    os.chdir('../..')
    projectDir = os.getcwd()
    projectName = os.path.basename(projectDir)

    os.chdir(projectSetDir)

    # load the file with the list of different component attributes
    compName = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compName'], 'value')
    compTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compTag'], 'value')
    compAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compAttr'], 'value')
    compValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compValue'], 'value')

    # get unique list of components
    compNameUnique = np.unique(compName)

    valSplit = [] # list of lists of attribute values
    for val in compValue: # iterate through all comonent attributes
        valSplit.append(val.split(',')) # split according along commas

    # get all possible combinations of the attribute values
    runValues = list(itertools.product(*valSplit))

    # get headings
    heading = [x + '.' + compTag[idx] + '.' + compAttr[idx] for idx, x in enumerate(compName)]

    # create dataframe and save as SQL
    df = pd.DataFrame(data = runValues, columns = heading)
    # add a column to indicate whether the simulation run has started. This is useful for when multiple processors are
    # running runs to avoid rerunning simulations. The column is called 'started'. 0 indicate not started and 1
    # indicates started
    df = df.assign(started=[0]*len(runValues))
    conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db') # create sql database
    df.to_sql('compAttributes', conn, if_exists="replace",index=False) # write to table compAttributes in db
    conn.close()

    # get the setup information for this set of simulations
    setupTag = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['setupAttributeValues', 'setupTag'], 'value')
    setupAttr = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['setupAttributeValues', 'setupAttr'], 'value')
    setupValue = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['setupAttributeValues', 'setupValue'],
                           'value')

    # copy the setup xml file to this simulation set directory and make the specified changes
    # if Setup dir does not exist, create
    if not os.path.exists(os.path.join(projectSetDir,'Setup')):
        os.mkdir(os.path.join(projectSetDir,'Setup'))
    # copy setup file
    setupFile = os.path.join(projectSetDir,'Setup',projectName + 'Set' + str(setNum) + 'Setup.xml')
    copyfile(os.path.join(projectDir,'InputData','Setup',projectName+'Setup.xml'), setupFile)

    # make the cbanges to it defined in projectSetAttributes
    for idx, val in enumerate(setupValue):  # iterate through all setup attribute values
        tag = setupTag[idx].split('.')
        attr = setupAttr[idx]
        value = val.split(',')
        writeXmlTag(setupFile, tag, attr, value)

    # get the components to be run
    components = readXmlTag(setupFile, 'componentNames', 'value')

    # generate the run directories
    for run, val in enumerate(runValues): # for each simulation run
        # check if there already is a directory for this run number.
        runDir = os.path.join(projectSetDir,'Run'+str(run))
        if not os.path.isdir(runDir):
            os.mkdir(runDir) # make run directory
            compDir = os.path.join(runDir, 'Components')
            os.mkdir(compDir) # make component directory
            # copy component descritors  and update
            for cpt in components: # for each component
                # copy from main input data
                copyfile(os.path.join(projectDir, 'InputData', 'Components', cpt + 'Descriptor.xml'),
                         os.path.join(compDir, cpt + 'Descriptor.xml'))
            # make changes
            for idx, value in enumerate(val):
                compFile = os.path.join(compDir, compName[idx] + 'Descriptor.xml')
                tag = compTag[idx].split('.')
                attr = compAttr[idx]
                # check if value is a tag in the xml document
                tryTagAttr = value.split('.') # split into tag and attribute
                # seperate into tags and attribute. There may be multiple tags
                tryTag = tryTagAttr[0]
                for i in tryTagAttr[1:-1]: # if there are any other tag values
                    tryTag = tryTag + '.' + i
                if tryTag in compTag:
                    tryAttr = tryTagAttr[-1] # the attribute
                    idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                    idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                    idxVal = list(set(idxTag).intersection(idxAttr))
                    value = val[idxVal[0]] # choose the first match, if there are multiple

                writeXmlTag(compFile, tag, attr, value)







