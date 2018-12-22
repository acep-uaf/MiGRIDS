# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 12, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag
import pandas as pd
import itertools
import sqlite3
from shutil import copyfile

def generateRuns(projectSetDir):
    here = os.getcwd()
    os.chdir(projectSetDir) # change directories to the directory for this set of simulations
    # get the set number
    dir_path = os.path.basename(projectSetDir)
    setNum = str(dir_path[3:])
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

    # check if wind turbine values were varied from base case. If so, will set the 'recalculateWtgPAvail' tag to 1
    # for each wind turbine
    #isWtg = any(['wtg' in x for x in compName])

    valSplit = [] # list of lists of attribute values
    for val in compValue: # iterate through all comonent attributes
        if not isinstance(val,list): # readXmlTag will return strings or lists, depending if there are commas. we need lists.
            val = [val]
        valSplit.append(val) # split according along commas

    # get all possible combinations of the attribute values
    runValues = list(itertools.product(*valSplit))

    # get headings
    heading = [x + '.' + compTag[idx] + '.' + compAttr[idx] for idx, x in enumerate(compName)]

    # get the setup information for this set of simulations
    setupTag = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['setupAttributeValues', 'setupTag'], 'value')
    setupAttr = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['setupAttributeValues', 'setupAttr'], 'value')
    setupValue = readXmlTag(projectName + 'Set'+str(setNum) + 'Attributes.xml', ['setupAttributeValues', 'setupValue'],
                           'value')

    # copy the setup xml file to this simulation set directory and make the specified changes
    # if Setup dir does not exist, create
    setupFile = os.path.join(projectSetDir, 'Setup', projectName + 'Set' + str(setNum) + 'Setup.xml')
    if os.path.exists(os.path.join(projectSetDir,'Setup')):
        inpt = input("This simulation set already has runs generated, overwrite? y/n")
        if inpt.lower() == 'y':
            generateFiles = 1
        else:
            generateFiles = 0
    if generateFiles == 1:
        os.mkdir(os.path.join(projectSetDir,'Setup'))
        # copy setup file
        copyfile(os.path.join(projectDir,'InputData','Setup',projectName+'Setup.xml'), setupFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(setupValue):  # iterate through all setup attribute values
            tag = setupTag[idx].split('.')
            attr = setupAttr[idx]
            value = val
            writeXmlTag(setupFile, tag, attr, value)

        # make changes to the predict Load input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'predictLoad')
        # make changes to the predict Wind input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'predictWind')
        # make changes to the reDispatch input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'reDispatch')
        # make changes to the getMinSrc input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'getMinSrc')
        # make changes to the gen dispatch
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'genDispatch')
        # make changes to the genSchedule input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'genSchedule')
        # make changes to the wtg dispatch input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'wtgDispatch')
        # make changes to the ees dispatch input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'eesDispatch')
        # make changes to the tes dispatch input file
        generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'tesDispatch')


    # get the components to be run
    components = readXmlTag(setupFile, 'componentNames', 'value')

    # generate the run directories
    runValuesUpdated = runValues # if any runValues are the names of another tag, then it will be updated here
    for run, val in enumerate(runValues): # for each simulation run
        # check if there already is a directory for this run number.
        runDir = os.path.join(projectSetDir,'Run'+str(run))
        compDir = os.path.join(runDir, 'Components')
        if not os.path.isdir(runDir):
            os.mkdir(runDir) # make run directory

            os.mkdir(compDir) # make component directory
        # copy component descriptors  and fillSetInfo
        for cpt in components: # for each component
            # copy from main input data
            copyfile(os.path.join(projectDir, 'InputData', 'Components', cpt + 'Descriptor.xml'),
                     os.path.join(compDir, cpt + 'Set' + str(setNum) + 'Run' + str(run) + 'Descriptor.xml'))


        # make changes
        for idx, value in enumerate(val):
            compFile = os.path.join(compDir, compName[idx] + 'Set' + str(setNum) + 'Run' + str(run) + 'Descriptor.xml')
            tag = compTag[idx].split('.')
            attr = compAttr[idx]
            # check if value is a tag in the xml document
            tryTagAttr = value.split('.')  # split into tag and attribute
            if len(tryTagAttr) > 1:
                # seperate into component, tags and attribute. There may be multiple tags
                tryComp = tryTagAttr[0]
                tryTag = tryTagAttr[1]
                for i in tryTagAttr[2:-1]: # if there are any other tag values
                    tryTag = tryTag + '.' + i
                tryAttr = tryTagAttr[-1]  # the attribute
                if tryComp in compName:
                    idxComp = [i for i, x in enumerate(compName) if x == tryComp]
                    idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                    idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                    idxVal = list(set(idxTag).intersection(idxAttr).intersection(idxComp))
                    value = val[idxVal[0]] # choose the first match, if there are multiple
                    a = list(runValuesUpdated[run]) # change values from tuple
                    a[idx] = value
                    runValuesUpdated[run] = tuple(a)
                else:
                    # check if it is referring to a tag in the same component
                    # seperate into tags and attribute. There may be multiple tags
                    tryTag = tryTagAttr[0]
                    for i in tryTagAttr[1:-1]:  # if there are any other tag values
                        tryTag = tryTag + '.' + i
                    if tryTag in compTag:
                        tryAttr = tryTagAttr[-1]  # the attribute
                        idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                        idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                        idxVal = list(set(idxTag).intersection(idxAttr))
                        value = val[idxVal[0]]  # choose the first match, if there are multiple
                        a = list(runValuesUpdated[run])  # change values from tuple
                        a[idx] = value
                        runValuesUpdated[run] = tuple(a)
            writeXmlTag(compFile, tag, attr, value)

            # if this is a wind turbine, then its values are being altered and the wind power time series will need
            # to be recalculated
            if 'wtg' in compName[idx]:
                if tag == 'powerCurveDataPoints' or tag == 'cutInWindSpeed' or tag == 'cutOutWindSpeedMax' or tag == 'cutOutWindSpeedMin' or tag == 'POutMaxPa':
                    writeXmlTag(compFile, 'recalculateWtgPAvail', 'value', 'True')

    # create dataframe and save as SQL
    df = pd.DataFrame(data=runValuesUpdated, columns=heading)
    # add columns to indicate whether the simulation run has started or finished. This is useful for when multiple processors are
    # running runs to avoid rerunning simulations. The columns are called 'started' and 'finished'. 0 indicate not
    # started (finished) and 1 indicates started (finished)
    df = df.assign(started=[0] * len(runValues))
    df = df.assign(finished=[0] * len(runValues))
    conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db')  # create sql database

    try:
        df.to_sql('compAttributes', conn, if_exists="fail", index=False)  # write to table compAttributes in db
    except sqlite3.Error as er:
        print(er)
        print('You need to delete the existing set ComponentAttributes.db before creating a new components attribute table')

    conn.close()
    os.chdir(here)


def generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, controlNameRoot):
    # make changes to the re dispatch input file, only if initializing the setup dir for this set. This avoids over
    # writing information
    # get the reDispatchInputsFile
    controlName = readXmlTag(setupFile, controlNameRoot, 'value')[0]
    controlInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                        projectName + controlName[0].upper() + controlName[1:] + 'Inputs.xml')

    # get the control inputs for this set of simulations
    controlInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                     [controlNameRoot+'InputAttributeValues', controlNameRoot+'InputTag'], 'value')
    controlInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                     [controlNameRoot+'InputAttributeValues', controlNameRoot+'InputAttr'], 'value')
    controlInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                      [controlNameRoot+'InputAttributeValues', controlNameRoot+'InputValue'],
                                      'value')

    # copy the reDispatchInput xml file to this simulation set directory and make the specified changes
    setControlInputFile = os.path.join(projectSetDir, 'Setup',
                                          projectName + 'Set' + str(setNum) + controlName[0].upper() + controlName[
                                                                                                      1:] + 'Inputs.xml')
    # copy controlInput file
    copyfile(controlInputsFile, setControlInputFile)
    # make the cbanges to it defined in projectSetAttributes
    for idx, val in enumerate(controlInputValue):  # iterate through all re dispatch attribute values
        tag = controlInputsTag[idx].split('.')
        attr = controlInputAttr[idx]
        value = val
        writeXmlTag(setControlInputFile, tag, attr, value)