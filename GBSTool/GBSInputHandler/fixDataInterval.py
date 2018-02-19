# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

#Reads a dataframe and ouputs a new dataframe with the specified sampling time interval.
#interval is a string with time units. (i.e. '30s' for 30 seconds, '1T' for 1 minute)
#If interval is less than the interval within the dataframe mean values are used to create a down-sampled dataframe
#DataClass, String -> dataframe
def fixDataInterval(data,interval):
    ''' data is a DataClass with a pandas dataframe with datetime index.
     interval is the desired interval of data samples. If this is 
     less than what is available in the df a lagevine estimator will be used to fill
     in missing times. If the interval is greater thant the original time interval
     the mean of values within the new interval will be generated'''
    import pandas as pd
    import sqlite3 as lite

   #local functions
   #generates a group id for groups of values within a series that are the same
   #Series -> Series
    def isInline(x):
        grouping = x.diff().ne(0).cumsum()
        return grouping
    
    #g is a row from from the groups dataframe, df is the dataframe containing component data
    #components is the list of power components within the dataframe
    #fills a specified block within a dataframe with simulated values
    #row, dataframe, list
    def langeEstimate(g,df,components):
        import numpy as np
        #the column containing a sum of power components
        s = df['total_p']
        #standard deviation of values before the missing values (excludes nan)
        sigma = np.std(s[:g['first']][-10:-1])
        
        #mean of values before the missing values (excludes nan)
        mu = np.mean(s[:g['first']][-10:-1]) 
        #previous total_p value is our start for estimating new values
        start = s[:g['first']][-2]  
        #estimateDistribution returns a list of times and values
        y = estimateDistribution(1,len(s[g['first']:g['last']]),start, mu,sigma,g['first'])           
        #this sets the total_p column to the new values
        s.loc[g['first']:g['last']]  = y[0] 
        #this distributes the total_p across all components
        #TODO if we only need power components change this to data.powerComponents
        for c in df.columns[0:-1]:
            #the adjuster is the proportion of total_p that a component was in the previous record
            adj = df.loc[:g['first'],c][-2]/df.loc[:g['first'],'total_p'][-2]
            df.loc[g['first']:g['last'],c] = round(adj * df.loc[g['first']:g['last'],'total_p'],0)
        return 
    
    #uses a langevin estimator to produce a specified number of 
    #values based on a start value, mean, and standard deviation 
    #elapsed_time is in seconds
    #int, numeric, numberic, numeric ->numeric array, numeric array
    def getValues(elapsed_time, start, mu, sigma):
        import numpy as np
        #seconds between samples
        timestep = 1
        #time constant
        tau = 3
        #number of steps 
        n = int(elapsed_time/timestep) + 1
        #vecter of times
        t=np.linspace(0.,elapsed_time,n)
        #renormalized variables
        sigma_bis = sigma * np.sqrt(2.0 / tau )
        sqrtdt = np.sqrt(timestep)
        #x is the array that will contain the new values
        x = np.zeros(n)
        #the starter value
        x[0] = start
    
        for i in range(n-1):
            x[i+1] = x[i] + timestep*(-(x[i]-mu)/tau) + sigma_bis * sqrtdt * (np.random.randn())
        x[x < 0] = 0
        #drop the starter value when the arrays are returned
        return t[1:], x[1:]
    # returns a list with 1 datetime array at specified intervals and 1 numeric array of simulated values          
    #int, int, numeric, numeric, numeric, datetime -> list
    def estimateDistribution(interval, records, start, mu, sigma,datetime):
       import pandas as pd 
       #get the estimated values
       t, x = getValues(records,start, mu, sigma)     
       #convert t to a range of times at the specified intervals
       t = pd.date_range(datetime - pd.to_timedelta(interval * records, unit='s'), periods=records,freq='s')
       #pair the time and values into a list to be returned
       distribution = [x[-records:],t[-records:]]
       return distribution
#TODO rempove sqlite backups      
#    database = 'fixedData0219.db'
#    connection = lite.connect(database)
    
    #make a copy of the input dataframe - original remains the same
    resample_df = pd.DataFrame(data.fixed.copy())
   
    #up or down sample to our desired interval
    #down sampling results in averaged values
    resample_df = resample_df.resample(interval).mean()
    #upsamping results in nan at new timesteps
    #make the nan's 0 for the total_p column so we can group it
    resample_df[pd.isnull(resample_df.total_p)] = 0
    resample_df['grouping']  = 0
    resample_df['grouping'] = isInline(resample_df.total_p)
    
    #create groups dataframe of repeated values
    groups = resample_df.reset_index().groupby('grouping').agg({resample_df.index.name:['count','first','last'],'total_p':['mean']})
    #remove the second column name level and keep only the groups where there is 0 for total_p
    groups.columns = groups.columns.droplevel(0)
    groups = groups[groups['mean'] ==0]
    
    #TODO remove loop through groups - only need for writing to sqlite
    previous_subgroup = 0
    for subgroup in range(10000, len(groups), 10000):
        print (subgroup)
        groups.loc[previous_subgroup:subgroup].apply(lambda x: langeEstimate(x,resample_df,data.powerComponents),axis = 1)
       
#        s = groups.iloc[previous_subgroup]['first']
#        e = groups.iloc[subgroup]['last']
#       if connection != None:
#            resample_df[s:e].to_sql("resampled_data",connection, if_exists='append')
        previous_subgroup = subgroup
    subgroup = len(groups)
    groups.iloc[previous_subgroup:subgroup].apply(lambda x: langeEstimate(x,resample_df,data.powerComponents),axis = 1)

    #check if there are 0's that came in for simulated total_p
    resample_df.loc[resample_df.total_p ==0,data.powerComponents] = None
    resample_df.loc[resample_df.total_p ==0,'total_p'] = None
    #fill with linear interpolation
    resample_df.total_p = resample_df.total_p.interpolate()
    #TODO remove sqlite backup
#    if connection != None:
#        resample_df.to_sql("resampled_data",connection, if_exists='replace')
    
    #put in a date column to be used when we convert to netcdf
    resample_df.insert(0, 'date', pd.to_numeric(resample_df.index))
    #drop temporary columns that won't be used in netCDF files
    resample_df = resample_df.drop('total_p',1)
    resample_df = resample_df.drop('grouping',1)
 
    return resample_df

