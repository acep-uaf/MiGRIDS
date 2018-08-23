import numpy as np
import pandas as pd
import datetime
# checkDataGaps looks for gaps in the timestamp index that is greater than the median sampling interval
# new records will have NA for values
# series -> series
def checkDataGaps(s):
    #calculate the median value for sample intervals and the duration between all intervals
    #the median inteval can be different for subsets of these data if multiple datasets were merged into one
    #m = medianInterval(s)
   
    
    timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff(periods=1)
    
    #shift it up so duration is to the next row
    timeDiff = timeDiff.shift(periods = -1)  
    medians = createMedians(timeDiff)
    timeDiff = pd.DataFrame(timeDiff)
    timeDiff['medians'] = medians   
    timeDiff.columns = ['timeDiff','medians']
    #local function to create datetime index
    #r is a row consisting of value and timedelta column named dif
    def makeIndex(r):
        
        d = pd.date_range(start =pd.to_datetime(r.name), periods=int(r['timeDiff']/r['medians']), freq=r['medians']).tolist()
        return [d,None]
    
    #filtered is a dataframe of values that need to be filled in because gaps in 
    #timestamps are greater than the median sample interval
    
    filtered = timeDiff[timeDiff['timeDiff'] > timeDiff['medians'] * 2]
    #ts = pd.Series(pd.to_datetime(filtered.index),index = filtered.index)
    #filtered = pd.concat([filtered,ts],axis=1, join='outer', keys=['dif','m','ts'])
    #list of missing timestamps for each indice in filtered
    missingIndices =filtered.apply(lambda r: makeIndex(r),axis=1)
    if len(missingIndices) > 0:
        #make the indices into a list of dataframes to be concatonated
        indices = missingIndices.iloc[:,0].apply(lambda i:pd.DataFrame(data = None,index = pd.DatetimeIndex(i))).tolist()
        
        s = s.append(pd.concat(indices))
    
        #only keep the colums we started with (return df to its original dimensions)
        s = s.iloc[:,0]
        #get rid of duplicate indices created by adding indices   
        s = s[~s.index.duplicated(keep='first')]
        #return a sorted dataframe
        s = s.sort_index(0, ascending=True) 
     
    return s
    
##series -> series  
#def medianInterval(s):
#   
#    timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff()
#    timeDiff = timeDiff.sort_index(0, ascending=True)
#    m = pd.to_timedelta(np.median(timeDiff),unit = 's')
#    return (m)

# series -> series
# returns the group id for values in the series, consecutive values will belong to the same group
def isInline(s):   
    #get rid of na's added through merging seperate files
    s = s.dropna()
    if len(s) > 0:
        #check for datagaps first. Datagaps are treated like inline data. 
        s = checkDataGaps(s)
        #na s identified in checkDataGaps get changed to a nonsense value so they will be grouped as inline data
        s = s.replace(np.nan,-99999)
        
        #group values that repeat over sampling intervals 
        grouping = s.diff().ne(0).cumsum()
       
        #we are only interested in the groups that have more than 1 record or are null
        groups = grouping.groupby(grouping).filter(lambda x: (sum(x) <= 0) or len(x) > 1)
        
        #return na values
        s = s.replace(-99999, np.nan)
        return groups
    
    return pd.Series(s)

#Dataframe,index, index-> list of Dataframe
def splitDataFrame(df,i1, d):
    newlist = [df[:i1][:-1],df[i1 + d:][1:]]
    return newlist

#splits a single dataframe into multiple dataframes based on absense of data for a specified cutoff interval
#ListOfDataframe, String, timedelta  ->Series  
def identifyCuts(lod, cname, cutoff, cutStarts):
    if (len(lod) <= 0):
        return cutStarts
    else:
        s = lod[0][cname]  
        s = s.dropna()
        timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff(periods=1)
        #shift it up so duration is to the next row  
        timeDiff = timeDiff.shift(periods = -1) 
        cutStarts = pd.concat([cutStarts,timeDiff[timeDiff >= cutoff]],axis=0)
        return identifyCuts(lod[1:],cname,cutoff,cutStarts)
    
#listofDataframe, listofString - > listOfDataFrames
def cutUpDataFrame(lod, loc):
    if len(loc)<=0:
        return lod
    else:
        cuts = identifyCuts(lod, loc[0], pd.Timedelta(weeks=2),pd.Series())
        lod = makeCuts(lod,cuts)
        return cutUpDataFrame(lod,loc[1:])

#cut is a series item
#load is a listofDataframes
def makeCut(lod, cut,newlist):
    if len(lod) <= 0:
        return None
    else:
        if (cut.index[0] in lod[0].index):
            newlist = splitDataFrame(lod[0],cut.index[0],cut[0]) + lod[1:] + newlist
            
            return newlist
        else:
            return makeCut(lod[1:],cut,newlist + lod[:1])
        
        
 #listOfDataframes, Series -> listOfDataFrames
def makeCuts(lod, cuts):
    if len(cuts) <= 0:
        return lod
    else:
       nl =  makeCut(lod,cuts[:1],[])
       if nl != None:
           return makeCuts(nl, cuts[1:])
       else:
           return makeCuts(lod, cuts[1:])
           
  #Timestamp, timedelta, Series with Timestamp index, Series with timestampindex
#initialTs is the timestamp for the beginning of the bad data
#d is the duration of the missing data
#possibles is a vector of possible starting points for replacement block
#s is the series with missing blocks to be replaced
#if a valid replacement block is not found the initial timestamp is returned
#inline values need to become na before this point
def findValid(initialTs, d, possibles, s):
    s = s.copy()
    s.loc[initialTs:initialTs + d,] = np.nan
    if len(possibles) < 1:
        return initialTs
    else:
        if len(s[pd.to_datetime(possibles.first_valid_index()):pd.to_datetime(possibles.first_valid_index()) + d].dropna()) < len(s[pd.to_datetime(possibles.first_valid_index()):pd.to_datetime(possibles.first_valid_index()) + d]):
            possibles = possibles[possibles.first_valid_index():][1:]
            return findValid(initialTs, d, possibles, s)
        else:
            return possibles[possibles.first_valid_index()]
            

    #first value is startof missing block
    #second value is end of missing block   
    #third value is list of possible replacement indices
#s is a series containing replacement values and matching indices to n
def validReplacements(n, s):
    if type(n['possibles']) is not list:
        return n['first']
    #n is the entire indicesOfinterest dataframe
    p = pd.Series(n['possibles'],index=n['possibles'])
    p = p[~p.index.duplicated(keep='first')]
    df = pd.concat([s,p],
               keys=['series','possibles'],
               axis=1, join='inner') 
    
    if type(s) is pd.DataFrame:
        df = df.drop(s.columns, axis=1, level=1)
        #get rid of level 1 index
        df.columns = df.columns.droplevel(1)
        
       
    diff = abs(pd.to_timedelta(df['possibles'] - pd.to_datetime(n['first'])))
    df['diff'] = diff
    df = df.sort_values('diff')
    p = df['possibles']
    v = findValid(n['first'], n['last']-n['first'], p, s)
    return v
#list of dataframes
def dropIndices(df, listOfRanges):
    if len(listOfRanges) <= 0:
        return df
    else:
       l = splitDataFrame(df,listOfRanges['first'].iloc[0], listOfRanges['last'].iloc[0] - listOfRanges['first'].iloc[0])
       if len(l)>1:
           df = l[0].append(l[1])
       return dropIndices(df,listOfRanges.iloc[1:])
   
#replace bad data in a dataframe starting with small missing blocks of data and moving to big blocks of missing data
#groups is a dataframe with column size, first and last
#cuts is a list of timedeltas
#df_to_fix is a subset of s that contains the portion of the dataframe that wil be fixed and passed on - can be equal to s
# s is the series or dataframe that replacement values are drawn from- can be larger or identical to df_ti_fix
#column is the column to be evaluated     
def doReplaceData(groups, df_to_fix, cuts, s):
    if(len(groups) <= 0):
        return df_to_fix
     #replace small missing chunks of data first, then large chunks
    else:
        groupsOfInterest = groups[groups['size'] <= cuts[0]]
        #indicesOfInterest = groupsOfInterest.index.to_series().groupby(groupsOfInterest['_'.join([column,'grouping'])]).agg(['first','last']).reset_index()
        indicesOfInterest = groupsOfInterest
        #s2 is our new values dataframe
        if len(indicesOfInterest) > 0:
            #we pass the original series to possibles so replacements can be found in data outside our truncated dataset
# =============================================================================
#             if type(s) == pd.DataFrame:
#                 indicesOfInterest['possibles'] = possibles(indicesOfInterest,s[column])
#             else:
#                 indicesOfInterest['possibles'] = possibles(indicesOfInterest,s)
#            #tod indices of interest should be all indices that are for groups of size less than cuttoff
# =============================================================================
            #convert datetimes to integers
            origin = s.first_valid_index()
            totalDuration = (s.last_valid_index() - origin).total_seconds()
            indicesSeconds = pd.DataFrame()
            indicesSeconds['first'] = (indicesOfInterest['first']-origin).astype('timedelta64[s]')
            indicesSeconds['last'] = (indicesOfInterest['last']-origin).astype('timedelta64[s]')
            print(datetime.datetime.now())
            indicesOfInterest.loc[:,'possibles'] = getPossibleStarts(indicesSeconds['first'], indicesSeconds['last'], origin, totalDuration)
            
            replacementStarts = indicesOfInterest.apply(lambda n: validReplacements(n, s), axis = 1)
            
            indicesOfInterest.loc[:,'replacementsStarts'] = replacementStarts
       
            #replace blocks of nas with blocks of replacementstarts
            df_to_fix = dropIndices(df_to_fix, indicesOfInterest)
            #new values get appended onto the datframe
            df_to_fix = expandDataFrame(indicesOfInterest,df_to_fix)
            
        return doReplaceData(groups[groups['size'] > cuts[0]],df_to_fix,cuts[1:],s)

#ioi is a single row from indicesOfInterest
#s is the series with na's removed
#returns a dataframe of same shape as s
def listsToDataframe(ioi,s):
    firstMissing = ioi['first']
    lastMissing = ioi['last']
    start = ioi['replacementsStarts']
    
    newBlock =s[start:start + (lastMissing - firstMissing)]
    
    if len(newBlock) > 0:
        timeFromStart = pd.Series(pd.to_datetime(newBlock.index)- pd.to_datetime(newBlock.index[0]))
        adjustedBlockTimes = timeFromStart + firstMissing 
        newBlock.index=adjustedBlockTimes
        #values that can't be replaced get returned to na and filled during upsampling
    else:
        newBlock = pd.DataFrame(index = pd.date_range(start=firstMissing,periods=2, 
                                                      freq =(lastMissing - firstMissing)))
        
       # newBlock.iloc[,0] = np.nan       
    
    return newBlock
#DataFrame,Series -> Series
#idf is a dataframe with first, last, and replacement start timestamps
def expandDataFrame(idf, s):
    if len(idf) <= 0:
        return s
    else:
        s = s.append(listsToDataframe(idf.iloc[0],s))
        s = s.sort_index()
        
        return expandDataFrame(idf.iloc[1:],s)  
#vector of integer -> vector of integer
#d is duration in seconds
#add of 5 days of search window for every day of missing data
#5 days of seconds = 432000
def getTimeRange(d):
    #days missing 
    days = round(d/86400, 0)
    days[days == 0] = 1
    days= days * 432000  
    return days
#returns a list of integer indices sorted by distance from s with lenght 2 * timeRange
#integer, integer -> listOfInteger
#s is start, timerange is searchrange
def createSearchRange(s,timeRange):
    fullRange = list(range(int(s),int(timeRange),1)) + list(range(int(s), int(s)-int(timeRange),-1))
    RangeAsSeries = pd.Series(fullRange, index = fullRange)
    #how far away from the origon a list item is
    RangeAsSeries = RangeAsSeries - s
    return RangeAsSeries.sort_values().index.tolist()
    
    
#missing index is vector of the first missing record start in seconds from origin
#timerange isa vector of the number of seconds of missing data
#origin is the starting datetime for the entire dataframe  
#totalDuration is the range of the entire dataset in seconds    
def getPossibleStarts(firstMissingIndex, lastMissingIndex, origin, totalDuration):
 # if there is a match then stop looking,
    # otherwise increment the search window by a year and look again
   
    #duration will be an integer of seconds of missing data
    duration = (lastMissingIndex- firstMissingIndex)
    smallBlock = duration < 1209600
    timeRange = getTimeRange(duration)
    firstMissingTimestamp = origin + pd.to_timedelta(firstMissingIndex, unit='s') #to timestamp
    # s is the first point we can start searching (attempts to go bakc as far as dataset will allow)
    #start and small block are vectors
    #make start and small block a dataframe
    dd = pd.DataFrame({'start':firstMissingIndex, 'smallBlock':smallBlock,'timeRange':timeRange,'totalDuration':totalDuration, 'firstMissingTimestamp':firstMissingTimestamp})
    dd = getStartYear(dd)
    #dd['startyear']= dd.apply(lambda n: cycleYear(n['start'],False,n['start'],n['smallBlock']), axis=1)
    dd.loc[:,'possibles'] = 0
    #this seems to be running three times per n
    dd.loc[:,'possibles'] = dd.apply(lambda n: calculateStarts([],n['smallBlock'],n['startyear'],n['start'], n['timeRange'], n['totalDuration'], origin)  ,axis=1)
    #possibles get filtered 
    return dd['possibles']
#DataFrame -> DataFrame
#input dataframe contains columns start for the start index of a mising block of data in seconds from beginning of dataset
#totalduration is the to time covered in the dataset
#smallBlock is whether the missing block is less than 2 weeks - boolean
def getStartYear(df):
    #subtract 
    df.loc[:,'startyear'] = df['start'] - 31536000 
     #if its still above 0 try subtracting again
    df.loc[(df['startyear'] > 0 ),'startyear'] = df['startyear'] - 31536000 
    
    #if it goes before the origin try increasing by a year
    df.loc[(df['startyear'] < 0 ),'startyear'] = df['startyear']+ 31536000 
   
    #anything still below zero go up again
    df.loc[(df['startyear'] < 0 ),'startyear'] = df['startyear'] + 31536000 
    #or any are big blocks and are now at the start year
    df.loc[(abs(df['startyear'] - df['start']) < 31536000) & (df['smallBlock'] == False),'startyear'] = df['startyear'] + 31536000 
    # if any are above the range acceptable - totalDuration go back down
    df.loc[(df['startyear'] > df['totalDuration'] ),'startyear'] = df['startyear'] - 31536000
    #if the difference between start year and start is less than a year and smallBlock is false startyear = np.nan
    df.loc[(abs(df['startyear'] - df['start']) < 31536000) & (df['smallBlock'] == False),'startyear']= np.nan
    return df
#returns of seriesof possible start points 
#possibles is the list of possible starts
#smallBlock is whether or not we are trying to fill a small or big block
#searchPoint is the index point we are evaluationg
#start is the original point we are trying to fill
#timeRange is how many seconds on either side of the searchpoint we want to include in possibles
#totalDuration is the maximum seconds from the start point that a dataframe contains
#list, boolean, integer, integer, integer, integer -> list
def calculateStarts(possibles, smallBlock, searchPoint, start, timeRange,totalDuration, origin):
    if searchPoint > totalDuration:
        p = pd.Series(possibles, index = possibles)
        possibles = pd.to_timedelta(p,unit = 's')
        
        i = origin + possibles 
        possibles.index = i  
        #go back to initial year
        return [filteredTimes(possibles, origin + pd.Timedelta(seconds = start))]
    elif np.isnan(searchPoint):
        return pd.Series([None])
    elif abs(searchPoint - start) > 31536000:
        return  calculateStarts(createSearchRange(searchPoint,10800), smallBlock, cycleYear(searchPoint,True,start, smallBlock),start, timeRange, totalDuration,origin)
    else:
        return  calculateStarts(createSearchRange(searchPoint,timeRange), smallBlock, cycleYear(searchPoint,True,start, smallBlock), start, timeRange, totalDuration,origin)

#returns a filtered series of datetimes that match the dayofweek and timeblocks of the missing timestamp
#possibles is a datatime index  
#returns list          
def filteredTimes(possibles,firstMissingTimestamp):
    #possibles is  a list of integers to start with
    #set the first value to 0 - this is our start point
    
    # restrict the search to only matching days of the week and time of day
    #day to match
    dayToMatch = firstMissingTimestamp.dayofweek
    
    possibles = possibles.between_time((firstMissingTimestamp - pd.Timedelta(hours=3)).time(),(firstMissingTimestamp + pd.Timedelta(hours=3)).time())
    possibles = pd.Series(pd.to_datetime(possibles.index), index= possibles.index)
    possibles =  possibles.dt.dayofweek
    #5 is a saturday
    if dayToMatch < 5:
        possibles = possibles[possibles < 5]
    else:
        possibles = possibles[possibles >= 5]
   
                                             
    #index of the remaining possibles is in seconds from origin
    return possibles.index.tolist()

def yearlyBreakdown(df):
    yearlies =df.index.to_series().groupby(df.index.year).agg(['first','last'])
    #find the closest offset
    yearlies['offset']= pd.Timedelta(days=7)
    yplus1= yearlies.shift(-1)
    yminus1=yearlies.shift(1)
    y = pd.concat([yearlies,yplus1.add_prefix('plus'),yminus1.add_prefix('minus')], axis=1)
    monthlies = df.index.to_series().groupby([df.index.year,df.index.month]).agg(['first','last'])
    y.index.rename('year', True)
    monthlies.index = monthlies.index.set_names(['year','month'])
    y = y.join(monthlies.add_prefix('month'), how='outer')
    #adjust years to match index years
    y.plusfirst = y.plusfirst + pd.Timedelta(days=-365)
    y.pluslast = y.pluslast + pd.Timedelta(days=-365)
    
    y.minusfirst = y.minusfirst + pd.Timedelta(days=365)
    y.minuslast = y.minuslast + pd.Timedelta(days=365)
    y.loc[((y.monthfirst >= y.minusfirst) &
      (y.monthfirst <=y.minuslast))
    & ((y.monthlast >= y.minusfirst) &
      (y.monthlast <=y.minuslast)), 'offset'] = pd.Timedelta(days=365)
    
    y.loc[((y.monthfirst >= y.plusfirst) &
      (y.monthfirst <=y.pluslast))
    & ((y.monthlast >= y.plusfirst) &
      (y.monthlast <=y.pluslast)), 'offset'] = pd.Timedelta(days=-365)
    
    f=y.monthfirst.groupby(y.offset).agg(['first','last'])
    l= y.monthlast.groupby(y.offset).agg(['first','last'])
    f['offset'] = f.index
    l['offset'] = l.index
    cuts = pd.DataFrame({'offset': l.offset, 'first' :f['first'], 'last' :l['last']})
    return cuts


#df is the complete dataset
#df_to_fix contains a subset of data deemed ok to use quick replace on
#gets fed in in chunks of the original dataframe depending on the offset to apply
#offset is a timedelta
#returns a dataframe of improved values with the same columns as the original input

def quickReplace(df,df_to_fix,offset,grouping):
    columns = df.columns
    grouping.name = 'grouping'  
    rcolumns = ["r" + c for c in columns]
    
    #reduce the dataset to just exclude na's unless they are new record fills (have a group id)    
    df_to_fix = pd.concat([df_to_fix,grouping],axis=1, join='outer')
    df_to_fix = df_to_fix[(np.isnan(df_to_fix[columns[0]]) & pd.notnull(df_to_fix['grouping']))|
                          (pd.notnull(df_to_fix[columns[0]]))]
    df_to_fix = df_to_fix.drop('grouping', axis=1)           
    
    df = pd.concat([df,grouping],axis=1, join='outer')
    df = df[(np.isnan(df[columns[0]]) & pd.notnull(df['grouping']))|
                          (pd.notnull(df[columns[0]]))]
    df = df.drop('grouping', axis=1)
    
    originalDOW = df.index[0].dayofweek
    #offset is backwards
    df = df.shift(periods=1,freq=offset, axis = 1)
    
    #check that the day of the week lines up and adjust if necessary
    diff = df.index[0].dayofweek-originalDOW
    if (diff == -1) | (diff == -6):
        df = df.shift(periods=1, freq = pd.Timedelta(days=1), axis=1)
    elif (diff == 1) | (diff == 6):
        df = df.shift(periods=1, freq = pd.Timedelta(days=-1), axis=1)
    elif (diff in([2,3,4,5,-2,-3,-4,-5])) :
        return
    mergedDf =pd.concat([df_to_fix,df.add_prefix('r')], axis = 1, join='outer')
    mergedDf[columns[0] + "copy"] = mergedDf[columns[0]]
    
    mergedDf = pd.concat([mergedDf,grouping], axis=1, join='outer')
    #if the row has been assigned to a group then it is a bad value and gets set to nan so it will be replaced
    mergedDf.loc[~np.isnan(mergedDf['grouping']),columns] = np.nan
    #rpelace all the bad values with the value at their offset position
    mergedDf.loc[(np.isnan(mergedDf[columns[0]])) & ~np.isnan(mergedDf.grouping) ,columns] =  mergedDf.loc[(np.isnan(mergedDf[columns[0]]))  & ~np.isnan(mergedDf.grouping),rcolumns].values
    #if not all the values within a group were replaced keep that group to be replaced later
    #badgroups are the ones where not every na was filled
    badGroups = mergedDf[np.isnan(mergedDf[columns[0]])]['grouping']
    
    #records belonging to a bad group get returned to Na to be replaced in a more complicated way
    mergedDf.loc[badGroups[pd.notnull(badGroups)].index,columns] = np.nan

    return mergedDf[columns],badGroups
    
    
#smallBlock indicates the missing block is less than 2 weeks - 1209600 seconds
#dt is the date we are adjust by a year
#up is whether to search up or down from our stop point
#dtStart is our original search start
#integer, Boolean, integer, Boolean
def cycleYear(dt, up, dtStart,smallBlock = True):            
    if up:
        t = dt + 31536000   #seconds in a year  
    else: 
       t = dt - 31536000
    if t < 0:
        return cycleYear(t,True,dtStart,smallBlock)
    #if its a big block missing and the test date is in the same year (less than 31536000 seconds away) 
    #bump the test start up a year
    if (t - dtStart < 31536000) & (smallBlock == False):
       return cycleYear(dt + 31536000, up,dtStart,smallBlock) 
    return t  

def createMedians(s):
    #Series of time diff values -> list of intervals that make up the majority of the dataset
    #returns a dataframe of group start and end indices and their sample interval
    def defineSampleInterval(s):
        f = s.quantile([0.25, 0.5, 0.85])
       
        l=f.tolist()
        
        l.sort()
        return l
    
    #DataFrame to be grouped, list of grouping intervals sorted lowest to highest
    #return dataframe of datasubset indices and their sampling intervals
    def createIntervalGroups(timeDiff,l):
        #timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff(periods=1)
        timeDiff[pd.to_timedelta(timeDiff) <= l[0] ] = l[0]
        for  i in range(1,len(l)):
            timeDiff[(pd.to_timedelta(timeDiff) <= l[i]) & (pd.to_timedelta(timeDiff) > l[i-1])] = l[i]
        timeDiff[pd.to_timedelta(timeDiff) > l[len(l)-1] ] = l[len(l)-1]  
        #s['timeDiff']= timeDiff
        #dataSubsets =s.index.to_series().groupby(s['timeDiff']).agg(['first','last'])
        return timeDiff
     
    l = list(set(defineSampleInterval(s)))
    medians = createIntervalGroups(s.copy(),l)
        
    return medians
    