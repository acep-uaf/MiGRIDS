# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)
# assumes the first column is always a date column
# reads data files from user and outputs a dataframe.
def readDataFile(inputFileType,fileLocation,fileType,columnNames,useNames,componentUnits,componentAttributes, dateColumnName, dateColumnFormat, timeColumnName, timeColumnFormat, utcOffsetValue, utcOffsetUnit, dst):
    # inputSpecification points to a script to accept data from a certain input data format *type string*
    # fileLocation is the dir where the data files are stored. It is either absolute or relative to the GBS project InputData dir *type string*
    # fileType is the file type. default is csv. All files of this type will be read from the dir *type string*
    # columnNames, if specified, is a list of column names from the data file that will be returned in the dataframe.
    # otherwise all columns will be returned. Note indexing starts from 0.*type list(string)*

    ####### general imports #######
    import pandas as pd
    from tkinter import filedialog
    import os
    import importlib.util
    import numpy as np
    from GBSInputHandler.readAllAvecTimeSeries import readAllAvecTimeSeries
    from GBSInputHandler.readWindData import readWindData
    from GBSAnalyzer.DataRetrievers.readXmlTag import readXmlTag
    from GBSInputHandler.Component import Component

    ### convert inputs to list, if not already
    if not isinstance(columnNames,(list,tuple,np.ndarray)):
        columnNames = [columnNames]
    if not isinstance(useNames, (list, tuple, np.ndarray)):
        useNames = [useNames]
    if not isinstance(componentUnits, (list, tuple, np.ndarray)):
        componentUnits = [componentUnits]
    if not isinstance(componentAttributes, (list, tuple, np.ndarray)):
        componentAttributes = [componentAttributes]

    ###### go to directory with time series data is located #######
    here = os.getcwd()
    if fileLocation=='':
        print('Choose directory where input data files are located.')
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost',1)
        fileLocation = filedialog.askdirectory()
    else:
        fileLocation = os.path.join(here,fileLocation)
    os.chdir(fileLocation)
    # get just the filenames ending with fileType. check for both upper and lower case
    # met files are text.
    if fileType.lower() == 'met':
        fileNames = [f for f in os.listdir(fileLocation) if
                     os.path.isfile(f) & (f.endswith('TXT') or f.endswith('txt'))]
    else:
        fileNames = [f for f in os.listdir(fileLocation) if
                     os.path.isfile(f) & (f.endswith(fileType.upper()) or f.endswith(fileType.lower()))]

    
    df = pd.DataFrame()
    ####### Parse the time series data files ############
    # depending on input specification, different procedure
    if inputFileType.lower() =='csv':
        df = readAllAvecTimeSeries(fileNames,fileLocation,columnNames,useNames,componentUnits, dateColumnName, dateColumnFormat, timeColumnName, timeColumnFormat, utcOffsetValue, utcOffsetUnit, dst)
    elif inputFileType.lower() == 'met':
        fileDict, df = readWindData(fileLocation,columnNames,useNames,componentUnits, dateColumnName, dateColumnFormat, timeColumnName, timeColumnFormat, utcOffsetValue, utcOffsetUnit, dst)
        
 
    
    # convert units
    if np.all(componentUnits != None):
        # initiate lists
        units = [None] * len(componentUnits)
        scale = [None] * len(componentUnits)
        offset = [None] * len(componentUnits)
        listOfComponents = []
        if componentAttributes != None:
            for i in range(len(componentUnits)): #for each channel make a component object
       
                # cd to unit conventions file
                dir_path = os.path.dirname(os.path.realpath(__file__))                
                unitConventionDir = os.path.join(dir_path, '../GBSAnalyzer/UnitConverters')
                # get the default unit for the data type
                units = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'units', unitConventionDir)[0]
                # if the units don't match, convert
                if units.lower() != componentUnits[i].lower():
                    unitConvertDir = os.path.join( dir_path,'../GBSAnalyzer/UnitConverters/unitConverters.py')
                    funcName = componentUnits[i].lower() + '2' + units.lower()
                    # load the conversion
                    spec = importlib.util.spec_from_file_location(funcName, unitConvertDir)
                    uc = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(uc)
                    x = getattr(uc, funcName)
                    # update data
                    df[useNames[i]] = x(df[useNames[i]])
                # get the scale and offset
                scale = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'scale',
                                   unitConventionDir)[0]
                offset = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'offset',
                                    unitConventionDir)[0]
                df[useNames[i]] = df[useNames[i]]*int(scale) + int(offset)
                # get the desired data type and convert
                datatype = readXmlTag('internalUnitDefault.xml', ['unitDefaults', componentAttributes[i]], 'datatype',
                                      unitConventionDir)[0]
                listOfComponents.append(Component(component_name=useNames[i],units=units,scale=scale,offset=offset,datatype=datatype,attribute=componentAttributes))

    # return to original directory
    os.chdir(here)
    return df, listOfComponents

