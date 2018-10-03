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

        # copy reDispatchInput file
        copyfile(getMinSRCInputsFile, setGetMinSRCInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(getMinSRCInputValue):  # iterate through all re dispatch attribute values
            tag = getMinSRCInputsTag[idx].split('.')
            attr = getMinSRCInputAttr[idx]
            value = val
            writeXmlTag(setGetMinSRCInputFile, tag, attr, value)



        # make changes to the genDispatch input file,
        # get the genDispatchInputsFile
        genDispatch = readXmlTag(setupFile, 'genDispatch', 'value')[0]
        getGenDispatchInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                           projectName + genDispatch[0].upper() + genDispatch[1:] + 'Inputs.xml')

        # get the gen dispatch inputs for this set of simulations
        getGenDispatchInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                        ['genDispatchInputAttributeValues', 'genDispatchInputTag'], 'value')
        getGenDispatchInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                        ['genDispatchInputAttributeValues', 'genDispatchInputAttr'], 'value')
        getGenDispatchInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                         ['genDispatchInputAttributeValues', 'genDispatchInputValue'],
                                         'value')

        # copy the genDispatchInput xml file to this simulation set directory and make the specified changes
        setGenDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                             projectName + 'Set' + str(setNum) + genDispatch[
                                                 0].upper() + genDispatch[1:] + 'Inputs.xml')
        # copy getMinSRCInput file
        copyfile(getGenDispatchInputsFile, setGenDispatchInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(getGenDispatchInputValue):  # iterate through all re dispatch attribute values
            tag = getGenDispatchInputsTag[idx].split('.')
            attr = getGenDispatchInputAttr[idx]
            value = val
            writeXmlTag(setGenDispatchInputFile, tag, attr, value)


        # make changes to the genSchedule input file,
        # get the genScheduleInputsFile
        genSchedule = readXmlTag(setupFile, 'genSchedule', 'value')[0]
        getGenScheduleInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                                projectName + genSchedule[0].upper() + genSchedule[
                                                                                       1:] + 'Inputs.xml')

        # get the gen Schedule inputs for this set of simulations
        getGenScheduleInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['genScheduleInputAttributeValues', 'genScheduleInputTag'], 'value')
        getGenScheduleInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['genScheduleInputAttributeValues', 'genScheduleInputAttr'], 'value')
        getGenScheduleInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                              ['genScheduleInputAttributeValues', 'genScheduleInputValue'],
                                              'value')

        # copy the genScheduleInput xml file to this simulation set directory and make the specified changes
        setGenScheduleInputFile = os.path.join(projectSetDir, 'Setup',
                                               projectName + 'Set' + str(setNum) + genSchedule[
                                                   0].upper() + genSchedule[1:] + 'Inputs.xml')
        # copy getMinSRCInput file
        copyfile(getGenScheduleInputsFile, setGenScheduleInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(getGenScheduleInputValue):  # iterate through all re Schedule attribute values
            tag = getGenScheduleInputsTag[idx].split('.')
            attr = getGenScheduleInputAttr[idx]
            value = val
            writeXmlTag(setGenScheduleInputFile, tag, attr, value)

        # make changes to the wtgDispatch input file,
        # get the wtgDispatchInputsFile
        wtgDispatch = readXmlTag(setupFile, 'wtgDispatch', 'value')[0]
        getWtgDispatchInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                                projectName + wtgDispatch[0].upper() + wtgDispatch[
                                                                                       1:] + 'Inputs.xml')

        # get the wtg dispatch inputs for this set of simulations
        getWtgDispatchInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['wtgDispatchInputAttributeValues', 'wtgDispatchInputTag'], 'value')
        getWtgDispatchInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['wtgDispatchInputAttributeValues', 'wtgDispatchInputAttr'], 'value')
        getWtgDispatchInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                              ['wtgDispatchInputAttributeValues', 'wtgDispatchInputValue'],
                                              'value')

        # copy the wtgDispatchInput xml file to this simulation set directory and make the specified changes
        setWtgDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                               projectName + 'Set' + str(setNum) + wtgDispatch[
                                                   0].upper() + wtgDispatch[1:] + 'Inputs.xml')
        # copy getWtgDispatchInput file
        copyfile(getWtgDispatchInputsFile, setWtgDispatchInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(getWtgDispatchInputValue):  # iterate through all re dispatch attribute values
            tag = getWtgDispatchInputsTag[idx].split('.')
            attr = getWtgDispatchInputAttr[idx]
            value = val
            writeXmlTag(setWtgDispatchInputFile, tag, attr, value)

        # make changes to the tesDispatch input file,
        # get the tesDispatchInputsFile
        tesDispatch = readXmlTag(setupFile, 'tesDispatch', 'value')[0]
        gettesDispatchInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                                projectName + tesDispatch[0].upper() + tesDispatch[
                                                                                       1:] + 'Inputs.xml')

        # get the tes dispatch inputs for this set of simulations
        gettesDispatchInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['tesDispatchInputAttributeValues', 'tesDispatchInputTag'], 'value')
        gettesDispatchInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['tesDispatchInputAttributeValues', 'tesDispatchInputAttr'], 'value')
        gettesDispatchInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                              ['tesDispatchInputAttributeValues', 'tesDispatchInputValue'],
                                              'value')

        # copy the tesDispatchInput xml file to this simulation set directory and make the specified changes
        settesDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                               projectName + 'Set' + str(setNum) + tesDispatch[
                                                   0].upper() + tesDispatch[1:] + 'Inputs.xml')
        # copy gettesDispatchInput file
        copyfile(gettesDispatchInputsFile, settesDispatchInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(gettesDispatchInputValue):  # iterate through all re dispatch attribute values
            tag = gettesDispatchInputsTag[idx].split('.')
            attr = gettesDispatchInputAttr[idx]
            value = val
            writeXmlTag(settesDispatchInputFile, tag, attr, value)


        # make changes to the eesDispatch input file,
        # get the eesDispatchInputsFile
        eesDispatch = readXmlTag(setupFile, 'eesDispatch', 'value')[0]
        getEesDispatchInputsFile = os.path.join(projectDir, 'InputData', 'Setup',
                                                projectName + eesDispatch[0].upper() + eesDispatch[
                                                                                       1:] + 'Inputs.xml')
        # get the ees dispatch inputs for this set of simulations
        getEesDispatchInputsTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['eesDispatchInputAttributeValues', 'eesDispatchInputTag'], 'value')
        getEesDispatchInputAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                             ['eesDispatchInputAttributeValues', 'eesDispatchInputAttr'], 'value')
        getEesDispatchInputValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                              ['eesDispatchInputAttributeValues', 'eesDispatchInputValue'],
                                              'value')

        # copy the eesDispatchInput xml file to this simulation set directory and make the specified changes
        setEesDispatchInputFile = os.path.join(projectSetDir, 'Setup',
                                               projectName + 'Set' + str(setNum) + eesDispatch[
                                                   0].upper() + eesDispatch[1:] + 'Inputs.xml')
        # copy geteesDispatchInput file
        copyfile(getEesDispatchInputsFile, setEesDispatchInputFile)
        # make the cbanges to it defined in projectSetAttributes
        for idx, val in enumerate(getEesDispatchInputValue):  # iterate through all re dispatch attribute values
            tag = getEesDispatchInputsTag[idx].split('.')
            attr = getEesDispatchInputAttr[idx]
            value = val
            writeXmlTag(setEesDispatchInputFile, tag, attr, value)


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




