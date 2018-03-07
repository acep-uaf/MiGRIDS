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
    from readAvecCsv import readAvecCsv
    from readXmlTag import readXmlTag

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
    if inputSpecification=='AVEC':
    # In the case of AVEC, data files are broken into months. Append them.
        for i in range(len(fileNames)): # for each data file
            if i == 0: # read data file into a new dataframe if first iteration
                df = readAvecCsv(fileNames[i],fileLocation,columnNames,useNames,componentUnits)
            else: # otherwise append
                df2 = readAvecCsv(fileNames[i],fileLocation,columnNames,useNames,componentUnits) # the new file
                # get intersection of columns,
                df2Col = df2.columns
                dfCol = df.columns
                #TODO: this does not maintain the order. It needs to be modified to maintain order of columns
                #dfNewCol = list(set(df2Col).intersection(dfCol))
                dfNewCol = [val for val in dfCol if val in df2Col]
                # resize dataframes to only contain columns contained in both dataframes
                df = df[dfNewCol]
                df2 = df2[dfNewCol]
                df = df.append(df2) # append
        
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
                                      unitConventionDir)
                listOfComponents.append(Component(useNames[i],units,scale,offset,datatype))

    # return to original directory
    os.chdir(here)
    return df, listOfComponents

#Component class consisting of component name, units and attribute
class Component:
    """A class with access to characteristics of a component."""
    def __init__(self, component, units, scale, offset, datatype):
        self.name = component
        self.units = units
        self.offset = offset
        self.datatype = datatype
        self.scale = scale
        

    def setDatatype(self,df):
         if self.datatype[0][0:3] == 'int':
             df[self.name] = round(df[self.name].astype('float'), 0)
         else:
             df[self.name] = df[self.name].astype(self.datatype[0])
         return df
    #Component, dictionary -> dictionary
    def toDictionary(self, d):
        d[self.name]= {
             'units':self.units,
             'offset':self.offset,
             'datatype':self.datatype,
             'scale':self.scale}

        return d