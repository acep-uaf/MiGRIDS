# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

#Reads a dataframe and ouputs a new dataframe with the specified sampling time interval.
#interval is a string with time units. (i.e. '30s' for 30 seconds, '1T' for 1 minute)
#If interval is less than the interval within the dataframe mean values are used to create a down-sampled dataframe
#If interval is greater than the interval within a dataframe linear interpolation is used to up-sample the dataframe
#Dataframe, String -> dataframe
def fixDataInterval(data,interval):
    # df is the pandas dataframe with a datetime index
    # interval is the desired interval of data samples. If this is significantly less than what is available in the df
    # (or for section of the df with missing measurements) upsampling methods will be used.
    import pandas as pd
    import sqlite3 as lite
    import numpy as np
    
    database = 'fixedData0219.db'
    connection = lite.connect(database)
    
    #make a copy of the database 
    resample_df = pd.DataFrame(data.fixed.copy())
    
    #these are our upsamping metrics
    #up or down sample to our desired interval
    resample_df = resample_df.resample(interval).mean()
    resample_df[pd.isnull(resample_df.total_p)] = 0
    resample_df['grouping']  = 0
    resample_df['grouping'] = isInline(resample_df.total_p)
    #create group objects of repeated values
    groups = resample_df.reset_index().groupby('grouping').agg({'DATE':['count','first','last'],'total_p':['mean']})
    groups.columns = groups.columns.droplevel(0)
    groups = groups[groups['mean'] ==0]
    previous_subgroup = 0
    for subgroup in range(10000, len(groups), 10000):
        print (subgroup)
        groups.loc[previous_subgroup:subgroup].apply(lambda x: langeEstimate(x,resample_df['total_p']),axis = 1)
       #TODODODODO
        s = groups.iloc[previous_subgroup]['first']
        e = groups.iloc[subgroup]['last']
        if connection != None:
            resample_df[s:e].to_sql("resampled_data",connection, if_exists='append')
        previous_subgroup = subgroup
    subgroup = len(groups) -1
    groups.loc[previous_subgroup:subgroup].apply(lambda x: langeEstimate(x,resample_df['total_p']),axis = 1)
    
    #zeros that came in during langevin estimation get filled with linear interpolation
#        resample_df.total_p.replace(0,np.nan)
    resample_df.total_p[resample_df.total_p ==0] = None
    resample_df.total_p = resample_df.total_p.interpolate()
           
    #x is index of missing row of data
    #df is dataframe with missingdata
    def fillProportion(x,df,c):
        #last valid value
        i = df.loc[:x,c].last_valid_index()
        lastx = df.loc[i,c]
        lasty = df.loc[i,'total_p']
        newvalue = lastx/lasty * df.loc[x,'total_p']
        return newvalue

    
    for c in data.powerComponents:
        resample_df[c] =  resample_df[pd.isnull(resample_df)].apply(lambda x: fillProportion(x.name,resample_df,c), axis = 1) 
   
    if connection != None:
        resample_df.to_sql("resampled_data",connection, if_exists='replace')
    
    #put in a date column to be used when we convert to netcdf
    resample_df.insert(0, 'date', resample_df.index.to_datetime())
    #get rid of the total p column
    resample_df = resample_df.drop('total_p',1)
    #set index to numeric
    resample_df.index = pd.to_numeric(resample_df.index)
    return resample_df

def isInline(x):
    grouping = x.diff().ne(0).cumsum()
    return grouping

#xis a grouping record, df is the dataframe containing values to replace
def langeEstimate(g,df):
   
    sigma = df[:g['first']][-10:].std()

    mu = df[:g['first']][-10:].mean()  
    start = df[:g['first']][-2]  
   
    dist = estimateDistribution(1,len(df[g['first']:g['last']]),start, mu,sigma,g['first'])           
    df.loc[g['first']:g['last']]  = dist[0] 
    return 
def getValues( elapsed_time, start, mu, sigma):
    import numpy as np
    #time constant
    timestep = 1
    #tau = 0.05
    tau = 3
    #number of steps 
    n = int(elapsed_time/timestep)
    #vecter of times
    t=np.linspace(0.,elapsed_time,n)
    #renormalized variables
    sigma_bis = sigma * np.sqrt(2.0 / tau )
    sqrtdt = np.sqrt(timestep)
    #number of states
    #each state windspeed

    x = np.zeros(n)
    
    x[0] = start

    for i in range(n-1):
        x[i+1] = x[i] + timestep*(-(x[i]-mu)/tau) + sigma_bis * sqrtdt * (np.random.randn())
    x[x < 0] = 0
    
    return t, x
            
  
def estimateDistribution(interval, records, start, mu, sigma,datetime):
   import pandas as pd 
   t, x = getValues(records,start, mu, sigma)     
   
   t = pd.date_range(datetime - pd.to_timedelta(interval * records, unit='s'), periods=records,freq='s')
   distribution = [x[-records:],t[-records:]]
   return distribution
  


