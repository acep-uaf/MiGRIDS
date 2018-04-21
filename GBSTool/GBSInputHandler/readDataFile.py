# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)
# assumes the first column is always a date column
# reads data files from user and outputs a dataframe.
def readDataFile(inputSpecification,fileLocation='',fileType='csv',columnNames=None,useNames=None,componentUnits=None,componentAttributes=None):
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
    from readAllAvecTimeSeries import readAllAvecTimeSeries
    from readWindData import readWindData
    from readXmlTag import readXmlTag
    from Component import Component

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
    # get just the filenames ending with fileType
    
    fileNames = [f for f in os.listdir(fileLocation) if os.path.isfile(f) & f.endswith(fileType)]
    
    df = pd.DataFrame()
    ####### Parse the time series data files ############
    # depending on input specification, different procedure
    if inputSpecification[0:4] =='AVEC':
       df = readAllAvecTimeSeries(fileNames,fileLocation,columnNames,useNames,componentUnits)
    if inputSpecification == 'AVECMulti':
        #read the wind data from a seperate file
        windfolder = os.path.join(fileLocation,'../../RawWindData')
        #winddf is a dataset at 1 second intervals
        winddf = readWindData(windfolder)
        #check if years match
        if winddf.date.year != df.date.year:
            ps = pd.Series(pd.to_datetime(winddf['time']))
            ps = ps.apply(lambda dt: dt.replace(year=df.year))
        #merge wind values with timeseries?? or generate wind file seperately?
        df = df.join(winddf)
        
    # try to convert to numeric
    df = df.apply(pd.to_numeric,errors='ignore')
    #order by datetime
    df = df.sort_values([df.columns[0]]).reset_index(drop=True)
    
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
                listOfComponents.append(Component(component_name=useNames[i],units=units,scale=scale,offset=offset,datatype=datatype))

    # return to original directory
    os.chdir(here)
    return df, listOfComponents

