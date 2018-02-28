# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

#Reads a dataframe and ouputs a new dataframe with the specified sampling time interval.
#interval is a string with time units. (i.e. '30s' for 30 seconds, '1T' for 1 minute)
#If interval is less than the interval within the dataframe mean values are used to create a down-sampled dataframe
#DataClass, String -> DataClass
def fixDataInterval(data,interval):
    ''' data is a DataClass with a pandas dataframe with datetime index.
     interval is the desired interval of data samples. If this is 
     less than what is available in the df a lagevine estimator will be used to fill
     in missing times. If the interval is greater thant the original time interval
     the mean of values within the new interval will be generated'''
    import pandas as pd
    

    #make a copy of the input dataframe - original remains the same
    resample_df = pd.DataFrame(data.fixed.copy())
    df = resample_df.copy()
    df['mu'] = df.total_p.rolling(10,2).mean()

    df['sigma'] = df.total_p.rolling(10,2).std()
    df['mu'] = df['mu'].bfill()
    df['sigma'] = df['sigma'].bfill()
    df['timediff']=pd.Series(pd.to_datetime(df.index),index=df.index).diff(1).shift(-1) 
    df['timediff'] = df['timediff'].fillna(0)
    #up or down sample to our desired interval
    #down sampling results in averaged values
    resample_df = resample_df.resample(interval).mean()
    def getValues(elapsed_time, start, mu, sigma):
        import numpy as np
        #seconds between samples
        timestep = 1
        
        #number of steps 
        n = (elapsed_time/timestep) + 1
        
        #renormalized variables
        sigma_bis = sigma * np.sqrt(2.0 / n )
        sqrtdt = np.sqrt(timestep)
        #x is the array that will contain the new values
        x = np.zeros(shape=(len(mu),int(max(n))))
        #the starter value
        x[:,0] = start
    
        for i in range(int(max(n)-1)):
            x[:,i+1] = x[:,i] + timestep*(-(x[:,i]-mu)/n) + sigma_bis * sqrtdt * (np.random.randn())
        
        #drop the starter value when the arrays are returned
        return x
        #upsamping results in nan at new timesteps
        #make the nan's 0 for the total_p column so we can group it
    def estimateDistribution(df):
       import numpy as np
        #feeders for the langevin estimate
       mu = df['mu']
       start = df['total_p']
       sigma = df['sigma']
       records = df['timediff']/pd.to_timedelta(interval)
       timestep = pd.Timedelta(interval).seconds
       
       #return an array of arrays of values
       y = getValues(records,start, mu, sigma)
       #steps is an array of timesteps in seconds with length = max(records)
       steps = np.arange(0, max(records)+1, timestep)
       #scaling
       #TODO get scaling from timestamp
       steps = steps * 1000000000
       #t is the numeric value of the dataframe timestamps
       t = pd.to_numeric(pd.to_datetime(df.index.values,unit='s')).values
 
       #intervals is the steps arrray repeated for every row of time
       intervals = np.repeat(steps,len(t), axis=0)
       #reshape the interval matrix so each row has every timestep
       intervals_reshaped = intervals.reshape(len(steps), len(t))
       tr = t.repeat(len(steps))
       rs = tr.reshape(len(t),len(steps))
       time_matrix = rs + intervals_reshaped.transpose()
       #put all the times in a single array
       time_array = np.concatenate(time_matrix)
       #put all the values in a single array
       values=np.concatenate(y)
       
      
       return time_array,values
       
    #t is the time, k is the estimated value
    t,k =estimateDistribution(df)
    simulated_df = pd.DataFrame({'time':t,'value':k})
    simulated_df= simulated_df.set_index(pd.to_datetime(simulated_df['time']))
    simulated_df = simulated_df[~simulated_df.index.duplicated(keep='last')]
    #join the simulated values to the upsampled dataframe by timestamp
    resample_df = resample_df.join(simulated_df,how='left')
    #fill na's for total_p with simulated values
    resample_df.loc[pd.isnull(resample_df['total_p']),'total_p'] = resample_df['value']
    #component values get calculated based on teh proportion that they made up previously
    adj_m = resample_df[resample_df.columns[0:-1]].div(resample_df['total_p'], axis=0)
    adj_m = adj_m.ffill()
    resample_df = adj_m.multiply(resample_df['total_p'], axis = 0)
     #put in a date column to be used when we convert to netcdf
    resample_df.insert(0, 'date', pd.to_numeric(resample_df.index))
    #get rid of columns added
    
    resample_df = resample_df.drop('time',1)
    resample_df = resample_df.drop('grouping',1)
        

    data.fixed = resample_df
    #data.removeAnomolies()
    return data
