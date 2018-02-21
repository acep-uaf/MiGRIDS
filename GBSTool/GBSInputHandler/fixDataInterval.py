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

    #make a copy of the input dataframe - original remains the same
    resample_df = pd.DataFrame(data.fixed.copy())
    df = resample_df.copy()
    df['mu'] = df.total_p.rolling(10,2).mean()

    df['sigma'] = df.total_p.rolling(10,2).std()
    df['mu'] = df['mu'].bfill()
    df['sigma'] = df['sigma'].bfill()
    #up or down sample to our desired interval
    #down sampling results in averaged values
    resample_df = resample_df.resample(interval).mean()
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
        return x
        #upsamping results in nan at new timesteps
        #make the nan's 0 for the total_p column so we can group it
    def estimateDistribution(x,df):
        #x.name is current location
       mu = x['mu']
       start = x['total_p']
       sigma = x['sigma']
       if df.loc[x.name:][1:].first_valid_index() != None:
           records = (df.loc[x.name:][1:].first_valid_index() - x.name) / interval
       else:
           return 
       y = getValues(records,start, mu, sigma) 
       y = y[1:-1]
       
       #convert t to a range of times at the specified intervals
       t = pd.date_range(x.name,  x.name + pd.to_timedelta(interval) * records, unit='s',freq='s')  
       t = t[1:-1]
    #pair the time and values into a list to be returned
       return t,y
       

    k =df.apply(lambda x: estimateDistribution(x,df), axis=1)
    nd = pd.DataFrame()
    for x in k:
        if x != None:
           nd =  nd.append(pd.DataFrame({'t':x[0],'y':x[1]}))
    nd= nd.set_index(nd['t'])
    resample_df = resample_df.join(nd,how='left')
    resample_df.loc[pd.isnull(resample_df['total_p']),'total_p'] = resample_df['y']
    adj_m = resample_df[resample_df.columns[0:-4]].div(resample_df['total_p'], axis=0)
    adj_m = adj_m.ffill()
    resample_df = adj_m.multiply(resample_df['total_p'], axis = 0)
      #put in a date column to be used when we convert to netcdf
    resample_df.insert(0, 'date', pd.to_numeric(resample_df.index))
    #drop temporary columns that won't be used in netCDF files
 
    return resample_df

