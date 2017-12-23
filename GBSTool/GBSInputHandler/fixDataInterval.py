# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def fixDataInterval(df,interval):
    # df is the pandas dataframe, where the first column is a dateTime column
    # interval is the desired interval of data samples. If this is significantly less than what is available in the df
    # (or for section of the df with missing measurements) upsampling methods will be used.

   
    # df_fixed is the fixed data (replaced bad data with approximated good data)
    df_fixed = pd.DataFrame()
    time_index = pd.to_datetime(df.iloc[:,0])
    #column 1 is the datetime
    for c in df.columns[1:]:
        ts = df[c]
        newvalues = seriesResample(ts,time_index,interval)
        df_fixed[c] = newvalues
    df_fixed.insert(0, 'date', newvalues.index.tolist())
    return df_fixed
    
def seriesResample(componentSeries,datetimeIndex, interval):
    componentSeries.index = datetimeIndex
    newValues = componentSeries.resample(interval).mean()
    #newValues.index = pd.to_numeric(newValues.index)
    nas = newValues[newValues.isnull()].index
    nv = linearFix(newValues.index,newValues,nas)
    return nv
    
def linearEstimate(x,y,t):
   
    k = stats.linregress(pd.to_numeric(x),pd.to_numeric(y))
    return  k.slope * t + k.intercept 

def linearFix(x,y,index_list):
     
     for i in index_list: 
         index = getIndex(y,i)
         value = linearEstimate(x[[min(index), max(index)+ 1],],
               y.iloc[[min(index),max(index)],], pd.to_numeric(x[x==i]))
         
         y.loc[i]=value.tolist()[0]
     return y
                    

# dataframe, integer, component -> integer list
#returns the closest 2 index valid values to i, i can range from 0 to len(df)
def getIndex(y, i):
    base = y.index.get_loc(i)
    #check if base is an int or array
    if isinstance(base,list):
        base = base[0]
    
    mask = pd.Index([base]).union(pd.Index([getNext(base,y,-1)])).union(pd.Index([getNext(base,y,1)]))
    #remove the original value from mask
    mask = mask.drop(base)
    return mask

#returns the position of the next value to use
#if we are given the 0 or last position the switch directions and take a bigger step
def getNext(i,y,step):
    try:
        if (y[i + step] == y[i + step]) & ((i + step) >= 0):
            
            return i + step
        elif (i + step) < 0:
            step = (2 * step) * -1
            return getNext(i,y,step)
        else:
            return getNext(i + step,y,step)
    except KeyError:
        step = (2 * step) * -1
        return getNext(i,y,step)
    
        
    
        


