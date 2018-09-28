from GBSInputHandler.readAvecCsv import readAvecCsv

def readAllAvecTimeSeries(inputDict):
    df = None
    for i in range(len(inputDict['fileNames'])):  # for each data file
        if i == 0:  # read data file into a new dataframe if first iteration
            inputDict['fileName'] = inputDict['fileNames'][i]
            df = readAvecCsv(inputDict)
        else:  # otherwise append
            df2 = readAvecCsv(inputDict)  # the new file
            # get intersection of columns,
            df2Col = df2.columns
            dfCol = df.columns
            # TODO: this does not maintain the order. It needs to be modified to maintain order of columns
            # dfNewCol = list(set(df2Col).intersection(dfCol))
            dfNewCol = [val for val in dfCol if val in df2Col]
            # resize dataframes to only contain columns contained in both dataframes
            df = df[dfNewCol]
            df2 = df2[dfNewCol]
            df = df.append(df2)  # append
    return df