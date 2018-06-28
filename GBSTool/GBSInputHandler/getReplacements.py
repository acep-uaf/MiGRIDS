
# TODO PERFORMANCE  slowest part of module because iterates through every missing interval
# dataframe, list of indices, string -> Boolean
# returns true if a replacement was made, false if it was not
def getReplacement(df, indices, columnsToReplace):
    import logging
    import pandas as pd
    import numpy as np
    from scipy import stats
    #constants
    # list of indices, dataframe, component -> dataframe
    # modifies the existing values in a dataframe using linear interpolation
    def linearFix(index_list, df, component):
        for i in index_list:
            index = getIndex(df[component], i)
            x = (pd.to_timedelta(pd.Series(df.index.to_datetime()))).dt.total_seconds().astype(int)
            x.index = pd.to_datetime(df.index, unit='s')
            y = df[component]
            value = linearEstimate(x[[min(index), max(index) + 1]],
                                   y[[min(index), max(index)]], x.loc[i])
            df.loc[i, component] = value
        return df


    # integer, Series, integer -> index
    # returns the closest valid index to i
    def getNext(i, l, step):
        if ((i + step) < 0) | ((i + step) >= len(l)):
            step = step * -2
            return getNext(i, l, step)
        elif not np.isnan(l[i + step]):
            return i + step
        else:
            return getNext((i + step), l, step)

    
    # Series, index -> list of indices
    # returns the closest 2 indices of valid values to i, i can range from 0 to len(df)
    def getIndex(y, i):
        base = y.index.get_loc(i)
        # check if base is an int or array, use first value if its a list
        if isinstance(base, list):
            base = base[0]
        mask = pd.Index([base]).union(pd.Index([getNext(base, y, -1)])).union(pd.Index([getNext(base, y, 1)]))
        # remove the original value from mask
        mask = mask.drop(base)
        return mask
    
    
    # numeric array, numeric array, Integer -> numeric
    # returns a linear estimated value for a given t value
    # x is array of x values (time), y is array of y values (power), t is x value to predict for.
    def linearEstimate(x, y, t):
        k = stats.linregress(x, y)
        return k.slope * t + k.intercept

    #returns the first valid index for the block to be used as replacement
    # index,range in same units as index, dataframe, dataframe, index -> index
    def getReplacementStart(dtStart, timeRange, entiredf, missingdf, columnsToEvaluate, directMatch=None):
     
        # if there is a match then stop looking,
        # otherwise increment the search window by a year and look again
        # start is the index of our first missing record
        start = missingdf.first_valid_index()
        duration = (missingdf.last_valid_index()- missingdf.first_valid_index())
        if duration >=pd.Timedelta('14 days'):
            print('big block')
        # searchBlock is the portion of the dataframe that we will search for a match in
        searchBlock = entiredf.loc[dtStart: dtStart + timeRange]
        # restrict the search to only matching days of the week and time of day
        searchBlock = searchBlock[(searchBlock.index.to_datetime().dayofweek == start.dayofweek)]
        searchBlock = searchBlock.between_time((start + pd.Timedelta(hours=3)).time(),
                                               (start - pd.Timedelta(hours=3)).time())
        group_name = missingdf['_'.join([columnsToEvaluate,'grouping'])][0]
        column = '_'.join([columnsToEvaluate,'grouping'])
        
        searchBlock = searchBlock[searchBlock[column] != group_name]
        
        #if the missing time frame is less than 2 weeks matchyear can be set to false
        # datetime, datetime, Boolean -> datetime
        def cycleYear(dt, dtStart, smallBlock = True):            
            t = dt + pd.DateOffset(years=1)      
            if (t - dtStart < pd.Timedelta(days=356)) & (smallBlock == False):
               return cycleYear(t,dtStart,smallBlock)
            else:
               return t
                
        # find the match in the searchBlock as long as it isn't empty
        if not searchBlock.empty:
            # order by proximity
            searchBlock['newtime'] = pd.Series(searchBlock.index.to_datetime(), searchBlock.index).apply(
                lambda dt: dt.replace(year=start.year))

            searchBlock['timeapart'] = searchBlock['newtime'] - start
            
            sortedSearchBlock = searchBlock.sort_values('timeapart')
            
            #BlockLength series is the indices of valid records in the evaluate column
            blockLength =  entiredf[min(sortedSearchBlock.index):max(sortedSearchBlock.index)]
            
            blockLength = blockLength[columnsToEvaluate].dropna()
            
            blockLength = pd.Series(pd.to_datetime(blockLength.index),index = blockLength.index)
            blockLength = blockLength.apply(lambda dt: longEnough(entiredf,blockLength,dt,duration))
            #flipped = part_of_df[::-1]
            #maxyear = max(entiredf.index) + pd.DateOffset(years=5)
           
            #flipped.index = maxyear - flipped.index 
            # if replacment is long enough return indices, otherwise move on
            #blockLength = flipped.rolling(duration).count()
            #blockLength = blockLength[::-1]
            #blockLength.index = part_of_df.index
            #print(blockLength.head())
            # a matching record is one that is the same day of the week, similar time of day and has enough
            # valid records following it to fill the empty block

            directMatch = blockLength.first_valid_index()
        # move the search window to the following year
        #if the missing timeframe is greater than 2 weeks don't search the current year
       
        dtStart = cycleYear(dtStart, start, duration <=pd.Timedelta('14 days'))
        
        searchBlock = entiredf[dtStart: dtStart + timeRange]
        
        # if we found a match return its index otherwise look again
        if directMatch is not None:
            return directMatch
        elif searchBlock.empty:
            # if theere is no where left to search return false
            return False
        else:
            
            # keep looking on the remainder of the list
            return getReplacementStart(dtStart, timeRange, entiredf, missingdf, columnsToEvaluate, directMatch)
   #returns true if a valid value is present in columnsToEvalueate for the entire duration from dt
   # dataframe, datetime, timedelta, string -> boolean
    def longEnough(df1, df2, dt, duration):
       return len(df1[dt: dt + duration]) == len(df2[dt: dt + duration])
    # dataframe, dataframe, dataframe, string -> dataframe
    # replaces a subset of data in a series with another subset of data of the same length from the same series
    # if component is total_p then replaces all columns with replacement data
    def dataReplace(df, missing, replacement, columnsToReplace):
        '''replaces the values in one dataframe with those from another'''
        #TODO join needs to be based on a column containing time from start record not time index
        #if ecolumns are empty they will get replaced along with power components, otherwise they will remain as they were.       
       #re-index the replacement data frame so datetimes match the dataframe's
        replacement.loc[:,'timediff'] = pd.Series(pd.to_datetime(replacement.index)).diff()
        replacement.index = replacement['timediff'] + min(df.index)
        
        df = df.join(replacement, how = 'outer', rsuffix=('replacement'))
        df.loc[min(missing.index):max(missing.index), columnsToReplace] = df.loc[min(missing.index):max(missing.index),[c + 'replacement' for c in columnsToReplace]]
        
        return df
    
    # dataframe, index, dataframe, string -> null
    # replaces a block of data and logs the indeces as bad records
    def replaceRecords(entiredf, dtStart, missingdf, columnsToReplace):
        window = missingdf.last_valid_index() - missingdf.first_valid_index()
        #this is the replacement block
        replacement = entiredf[dtStart:dtStart + window]
        
        logging.info("replaced inline values %s through %s with %s through %s."
                     % (str(min(missingdf.index)), str(max(missingdf.index)), str(min(replacement.index)),str(max(replacement.index))))
        df= dataReplace(entiredf, missingdf,replacement,columnsToReplace)
        return df


    # dataframe -> index, timedelta
    # returns the a window of time that should be searched for replacement values depending on the
    # amount of time covered in the missing block
    def getMoveAndSearch(missingdf):
        
        # for large missing blocks of data we use a larger possible search range
        if (missingdf.index.max() - missingdf.index.min()) >= pd.Timedelta('1 days'):
            initialMonths = 2
            timeRange = pd.DateOffset(months=4)
        else:
            initialMonths = 1
            timeRange = pd.DateOffset(weeks=8)
        # start is the missingblock minus a year and the searchrange
        dtStart = missingdf.index[0] - pd.DateOffset(years=1, months=initialMonths, days=14)
        return dtStart, timeRange

    # get the block of missing data
    missingBlock = df.loc[indices]
    # search start is datetime indicating the start of the block of data to be searched
    # searchRange indicates how big of a block of time to search
    searchStart, searchRange = getMoveAndSearch(missingBlock)
    
    # replacementStart is a datetime indicating the first record in the block of replacementvalues
    #it is assumed that the first value in columns to Replace is the column that is being evaluated
    replacementStart = getReplacementStart(searchStart, searchRange, df, missingBlock, columnsToReplace[0])
    if replacementStart:       
        # replace the bad records
        entiredf = replaceRecords(df, replacementStart, missingBlock, columnsToReplace)
        if len(entiredf) > 0:
            return True
        else:
            return False
    elif len(missingBlock) <= 15:
        # if we didn't find a replacement and its only a few missing records use linear estimation
        index_list = missingBlock.index.tolist()
        linearFix(index_list, df, columnsToReplace[0])
        logging.info("No similar data subsets found. Using linear interpolation to replace inline values %s through %s."
                     % (str(min(missingBlock.index)), str(max(missingBlock.index))))
        return True
    else:
        logging.info(
            "could not replace values %s through %s." % (str(min(missingBlock.index)), str(max(missingBlock.index))))
        return False
    
    




