from MicroGRIDS.InputHandler.readCsv import readCsv

def readAllTimeSeries(inputDict):
    '''
    Cycles through a list of files in the AVEC format and imports them into a single dataframe.
    :param inputDict:
    :return: pandas.DataFrame with data from all input files.
    '''
    df = None
    for i in range(len(inputDict['fileNames'])): 
        print(inputDict['fileNames'][i])# for each data file
        inputDict['fileName'] = inputDict['fileNames'][i]
        if i == 0:  # read data file into a new dataframe if first iteration
            
            df = readCsv(inputDict)
        else:  # otherwise append
            df2 = readCsv(inputDict)  # the new file
            # get intersection of columns,
            df2Col = df2.columns
            dfCol = df.columns

            dfNewCol = [val for val in dfCol if val in df2Col]
            # resize dataframes to only contain columns contained in both dataframes
            df = df[dfNewCol]
            df2 = df2[dfNewCol]
           
            df = df.append(df2)  # append
            
    df = df.sort_values('DATE')
    
    return df

