# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 12, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
from GBSAnalyzer.DataRetrievers.readXmlTag import readXmlTag
from GBSInputHandler.writeXmlTag import writeXmlTag
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
    if not os.path.exists(os.path.join(projectSetDir,'Setup')):
        os.mkdir(os.path.join(projectSetDir,'Setup'))
        # copy setup file
        copyfile(os.path.join(projectDir,'InputData','Setup',projectName+'Setup.xml'), setupFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(setupValue):  # iterate through all setup attribute values
            tag = setupTag[idx].split('.')
            attr = setupAttr[idx]
            value = val
            writeXmlTag(setupFile, tag, attr, value)

        # make changes to the re dispatch input file, only if initializing the setup dir for this set. This avoids over
        # writing information
        # get the reDispatchInputsFile
        reDispatch = readXmlTag(setupFile, 'reDispatch', 'value')[0]
        reDispatchInputsFile = os.path.join(projectDir, 'InputData', 'Setup', projectName + reDispatch[0].upper() + reDispatch[1:] + 'Inputs.xml')

        # get the RE dispatch inputs for this set of simulations
        reDispatchInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                              ['reDispatchInputAttributeValues', 'reDispatchInputTag'], 'value')
        reDispatchInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                               ['reDispatchInputAttributeValues', 'reDispatchInputAttr'], 'value')
        reDispatchInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                ['reDispatchInputAttributeValues', 'reDispatchInputValue'],
                                'value')

        # copy the reDispatchInput xml file to this simulation set directory and make the specified changes
        setReDispatchInputFile = os.path.join(projectSetDir, 'Setup', projectName + 'Set' + str(setNum) + reDispatch[0].upper() + reDispatch[1:] + 'Inputs.xml')
        # copy reDispatchInput file
        copyfile(reDispatchInputsFile, setReDispatchInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(reDispatchInputValue):  # iterate through all re dispatch attribute values
            tag = reDispatchInputsTag[idx].split('.')
            attr = reDispatchInputAttr[idx]
            value = val
            writeXmlTag(setReDispatchInputFile, tag, attr, value)

        # make changes to the genMinSRC input file,
        # get the reDispatchInputsFile
        getMinSRC = readXmlTag(setupFile, 'getMinSrc', 'value')[0]
        getMinSRCInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                            projectName + getMinSRC[0].upper() + getMinSRC[1:] + 'Inputs.xml')

        # get the RE dispatch inputs for this set of simulations
        getMinSRCInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                         ['getMinSRCInputAttributeValues', 'getMinSRCInputTag'], 'value')
        getMinSRCInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                         ['getMinSRCInputAttributeValues', 'getMinSRCInputAttr'], 'value')
        getMinSRCInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                          ['getMinSRCInputAttributeValues', 'getMinSRCInputValue'],
                                          'value')

        # copy the reDispatchInput xml file to this simulation set directory and make the specified changes
        setGetMinSRCInputFile = os.path.join(projectSetDir, 'Setup',
                                              projectName + 'Set' + str(setNum) + getMinSRC[
                                                  0].upper() + getMinSRC[1:] + 'Inputs.xml')
        # copy getMinSRCInput file
        copyfile(getMinSRCInputsFile, setGetMinSRCInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(getMinSRCInputValue):  # iterate through all re dispatch attribute values
            tag = getMinSRCInputsTag[idx].split('.')
            attr = getMinSRCInputAttr[idx]
            value = val
            writeXmlTag(setGetMinSRCInputFile, tag, attr, value)






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
            # check to see if any mathematical operations are required
            tryTagAttr = value.split('+')  # check for addition
            tryTagAttr = [x.split('-') for x in tryTagAttr]  # subtraction
            tryTagAttr = [[x.split('*') for x in y] for y in tryTagAttr]  # multiplication
            tryTagAttr = [[[x.split('/') for x in y] for y in z] for z in tryTagAttr]  # division

            # the value to be written
            writeVal = 0
            for idxA,a in enumerate(tryTagAttr): # all addends
                for idxS,s in enumerate(a): # all subtrahends
                    for idxF,f in enumerate(s): # all factors
                        for idxD,d in enumerate(f): # all dividends
                            # check if this is possibly refering to another tag's value
                            # split by '.' and see if corresponds to a component or tag name
                            tryDTag = d.split('.')
                            if len(tryDTag) > 1:
                                # seperate into component, tags and attribute. There may be multiple tags
                                tryComp = tryDTag[0]
                                tryTag = tryDTag[1]
                                for i in tryDTag[2:-1]:  # if there are any other tag values
                                    tryTag = tryTag + '.' + i
                                tryAttr = tryDTag[-1]  # the attribute
                                if tryComp in compName:
                                    idxComp = [i for i, x in enumerate(compName) if x == tryComp]
                                    idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                                    idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                                    idxVal = list(set(idxTag).intersection(idxAttr).intersection(idxComp))
                                    d = val[idxVal[0]]  # choose the first match, if there are multiple

                                else:
                                    # check if it is referring to a tag in the same component
                                    # seperate into tags and attribute. There may be multiple tags
                                    tryTag = tryDTag[0]
                                    for i in tryDTag[1:-1]:  # if there are any other tag values
                                        tryTag = tryTag + '.' + i
                                    if tryTag in compTag:
                                        tryAttr = tryDTag[-1]  # the attribute
                                        idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                                        idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                                        idxVal = list(set(idxTag).intersection(idxAttr))
                                        d = val[idxVal[0]]  # choose the first match, if there are multiple

                            # divide
                            if idxD ==0:
                                f = d
                            else:
                                # round to 4 decimal places since floats are not exact and operations can result in a lot
                                # of decimal places.
                                f = round(float(f) / float(d),4)
                        # multipy
                        if idxF == 0:
                            s = f
                        else:
                            s = round(float(s) * float(f),4)
                    # subtract
                    if idxS == 0:
                        a = s
                    else:
                        a = round(float(a) - float(s),4)
                # add
                if idxA == 0:
                    writeVal = a
                else:
                    writeVal = round(float(writeVal) + float(a),4)

            temp = list(runValuesUpdated[run])  # change values from tuple
            temp[idx] = writeVal
            runValuesUpdated[run] = tuple(temp)
            writeXmlTag(compFile, tag, attr, writeVal)

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




