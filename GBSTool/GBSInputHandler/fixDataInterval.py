# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

#Reads a dataframe and ouputs a new dataframe with the specified sampling time interval.
#interval is a string with time units. (i.e. '30s' for 30 seconds, '1T' for 1 minute)
#If interval is less than the interval within the dataframe mean values are used to create a down-sampled dataframe
#DataClass, String -> DataClass
def fixDataInterval(data, interval):
    ''' data is a DataClass with a pandas dataframe with datetime index.
     interval is the desired interval of data samples. If this is 
     less than what is available in the df a langevin estimator will be used to fill
     in missing times. If the interval is greater thant the original time interval
     the mean of values within the new interval will be generated'''
    import pandas as pd


    #df contains the non-upsampled records. Means and standard deviation come from non-upsampled data.
    df = data.fixed.copy()
    #mean
    df['mu'] = df.total_p.rolling(10, 2).mean()
    #standard deviation
    df['sigma'] = df.total_p.rolling(10, 2).std()
    #first records get filled with first valid values of mean and standard deviation
    df['mu'] = df['mu'].bfill()
    df['sigma'] = df['sigma'].bfill()
    #time interval between consecutive records
    df['timediff'] = pd.Series(pd.to_datetime(df.index, unit='s'), index=df.index).diff(1).shift(-1)
    df['timediff'] = df['timediff'].fillna(0)

    #up or down sample to our desired interval
    #down sampling results in averaged values
    data.fixed = data.fixed.resample(interval).mean()

    #integer, numeric, numeric, numeric -> numeric array
    #uses the Langevin equation to estimate records based on provided mean (mu) and standard deviation and a start value
    def getValues(records, start, mu, sigma):
        import numpy as np
        #seconds between samples
        timestep = 1

        #number of steps 
        n = (records / timestep) + 1

        #renormalized variables
        sigma_bis = sigma * np.sqrt(2.0 / n)
        sqrtdt = np.sqrt(timestep)
        #x is the array that will contain the new values
        x = np.zeros(shape=(len(mu), int(max(n))))
        #the starter value
        x[:, 0] = start

        for i in range(int(max(n) - 1)):
            x[:, i + 1] = x[:, i] + timestep * (-(x[:, i] - mu) / n) + sigma_bis * sqrtdt * (np.random.randn())

        return x

    #dataframe -> integer array, integer array
    #returns arrays of time as seconds and values estimated using the Langevin equation
    #for all gaps of data within a dataframe
    def estimateDistribution(df):
        import numpy as np
        #feeders for the langevin estimate
        mu = df['mu']
        start = df['total_p']
        sigma = df['sigma']
        records = df['timediff'] / pd.to_timedelta(interval)
        timestep = pd.Timedelta(interval).seconds

        #return an array of arrays of values
        y = getValues(records, start, mu, sigma)
        #steps is an array of timesteps in seconds with length = max(records)
        steps = np.arange(0, max(records) + 1, timestep)

        #t is the numeric value of the dataframe timestamps
        t = pd.to_timedelta(pd.to_datetime(df.index.values, unit='s')).dt.total_seconds()

        #intervals is the steps array repeated for every row of time
        intervals = np.repeat(steps, len(t), axis=0)
        #reshape the interval matrix so each row has every timestep
        intervals_reshaped = intervals.reshape(len(steps), len(t))
        tr = t.repeat(len(steps))
        rs = tr.reshape(len(t), len(steps))
        time_matrix = rs + intervals_reshaped.transpose()
        #put all the times in a single array
        timeArray = np.concatenate(time_matrix)
        #put all the values in a single array
        values = np.concatenate(y)

        return timeArray, values

    #t is the time, k is the estimated value
    t, k = estimateDistribution(df)
    simulatedDf = pd.DataFrame({'time': t, 'value': k})
    simulatedDf = simulatedDf.set_index(pd.to_datetime(simulatedDf['time']))
    simulatedDf = simulatedDf[~simulatedDf.index.duplicated(keep='last')]
    #join the simulated values to the upsampled dataframe by timestamp
    data.fixed = data.fixed.join(simulatedDf, how='left')
    #fill na's for total_p with simulated values
    data.fixed.loc[pd.isnull(data.fixed['total_p']), 'total_p'] = data.fixed['value']
    #component values get calculated based on the proportion that they made up previously
    adj_m = data.fixed[data.fixed.columns[0:-1]].div(data.fixed['total_p'], axis=0)
    adj_m = adj_m.ffill()
    data.fixed = adj_m.multiply(data.fixed['total_p'], axis=0)

    #get rid of columns added
    data.fixed = data.fixed.drop('time', 1)
    data.fixed = data.fixed.drop('grouping', 1)

    data.removeAnomolies()
    return data
