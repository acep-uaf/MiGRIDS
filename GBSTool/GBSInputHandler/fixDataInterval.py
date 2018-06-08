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
     in missing times. If the interval is greater than the original time interval
     the mean of values within the new interval will be generated'''
    import pandas as pd
    import numpy as np



    #integer, numeric, numeric, numeric -> numeric array
    #uses the Langevin equation to estimate records based on provided mean (mu) and standard deviation and a start value
    def getValues(records, start, sigma, timestep):
        # sigma is the the standard deviation for 1000 samples at timestep interval
        import numpy as np


        #number of steps 
        n = (records / timestep) + 1
        # time constant. This value was empirically determined to result in a mean value between
        tau = records*.2


        #renormalized variables
        # TODO: look at sigma calculation
        # sigma scaled takes into account the difference in STD for different number of samples of data. Given a STD for
        # 1000 data samples (sigma) the mean STD that will be observed is sigmaScaled, base empirically off of 1 second
        # Igiugig data for 1 year.
        sigmaScaled = sigma * (0.0158*np.log(n)**2 + 0.0356*np.log(n))
        #sigmaScaled = sigma
        sigma_bis = sigmaScaled * np.sqrt(2.0 / n) # adapted from ipython interactive computing visualization cookbook
        sqrtdt = np.sqrt(timestep)
        # find the 95th percentile of number of steps
        n95 = int(np.percentile(n,95))
        # find where over the 95th percentile
        idxOver95 = np.where(n > n95)
        #x is the array that will contain the new values
        x = np.zeros(shape=(len(start), int(n95)))

        # steps is an array of timesteps in seconds with length = max(records)
        steps = np.arange(0, int(n95)*timestep, timestep)
        # t is the numeric value of the dataframe timestamps
        t = pd.to_timedelta(pd.Series(pd.to_datetime(start.index.values, unit='s'), index=start.index)).dt.total_seconds()
        # intervals is the steps array repeated for every row of time
        intervals = np.repeat(steps, len(t), axis=0)
        # reshape the interval matrix so each row has every timestep
        intervals_reshaped = intervals.reshape(len(steps), len(t))
        # TODO: MemoryError here
        tr = t.repeat(len(steps))
        rs = tr.reshape(len(t), len(steps))
        time_matrix = rs + intervals_reshaped.transpose()
        # put all the times in a single array
        timeArray = np.concatenate(time_matrix)

        #the starter value
        x[:, 0] = start
        # use the next step in the time series as the average value for the synthesized data. The values will asympotically reach this value, resulting in a smooth transition.
        mu = start.shift(-1)
        mu.iloc[-1] = mu.iloc[-2]

        for i in range(n95-1):
            x[:, i + 1] = x[:, i] + timestep * (-(x[:, i] - mu) / tau) + np.multiply(sigma_bis.values * sqrtdt, np.random.randn(len(mu)))

        values = np.concatenate(x)

        # individually calc the rest
        for idx in idxOver95:
            # find remaining values to be calculated
            nRemaining = int(max([n[idx].values[0] - n95, 0]))
            # calc remaining values
            x0 = np.zeros(shape = (nRemaining,))
            # first value is last value of array
            x0[0] = x[idx, -1]

            # corresponding time matrix
            time_matrix0 = time_matrix[idx,-1] + np.arange(0,nRemaining*timestep,timestep)
            for idx0 in range(1,nRemaining):
                x0[idx0] = x0[idx0-1] + timestep * (-(x0[idx0-1] - mu[idx]) / tau[idx]) + np.multiply(sigma_bis.values[idx] * sqrtdt, np.random.randn())

            # append to already calculated values
            values = np.append(values, x0)
            timeArray = np.append(timeArray,time_matrix0)

        # TODO: sort values and timeArray by TimeArray
        tv = zip(timeArray,values)
        tv = tv[tv[:,0].argsort()] # sort by timeArray

        t, v = zip(*tv)

        return t,v

    #dataframe -> integer array, integer array
    #returns arrays of time as seconds and values estimated using the Langevin equation
    #for all gaps of data within a dataframe
    def estimateDistribution(df,interval,col):
        import numpy as np
        #feeders for the langevin estimate
        mu = df[col+'_mu']
        start = df[col]
        sigma = df[col+'_sigma']
        records = df['timediff'] / pd.to_timedelta(interval)
        timestep = pd.Timedelta(interval).seconds

        #return an array of arrays of values
        y = getValues(records, start, sigma,timestep)
        #steps is an array of timesteps in seconds with length = max(records)
        steps = np.arange(0, max(records) + 1, timestep)

        #t is the numeric value of the dataframe timestamps
        t = pd.to_timedelta(pd.Series(pd.to_datetime(df.index.values, unit='s'),index=df.index)).dt.total_seconds()
        # test if the index can be interpreted as datetime, if not recognized, convert
        #try:
        #    t = pd.to_timedelta(pd.Series(df.index.values)).dt.total_seconds()
        #except ValueError:
        #    t = pd.to_timedelta(pd.Series(pd.to_datetime(df.index.values, unit='s'), index=df.index)).dt.total_seconds()
        #intervals is the steps array repeated for every row of time
        intervals = np.repeat(steps, len(t), axis=0)
        #reshape the interval matrix so each row has every timestep
        intervals_reshaped = intervals.reshape(len(steps), len(t))
        # TODO: MemoryError here
        tr = t.repeat(len(steps))
        rs = tr.reshape(len(t), len(steps))
        time_matrix = rs + intervals_reshaped.transpose()
        #put all the times in a single array
        timeArray = np.concatenate(time_matrix)
        #put all the values in a single array
        values = np.concatenate(y)

        return timeArray, values

    # df contains the non-upsampled records. Means and standard deviation come from non-upsampled data.
    df = data.fixed.copy()

    # find non power columns
    # create a list of non power columns (column names not ending in p)
    fixColumns = []
    for col in data.fixed.columns:
        if col.lower()[-1:] != 'p':
            fixColumns.append(col)

    # a list of all non-power columns and the total power. Removes and other power columns
    fixColumns.append('total_p')

    # up or down sample to our desired interval
    # down sampling results in averaged values
    data.fixed = data.fixed.resample(pd.to_timedelta(interval)).mean()

    for col in fixColumns:
        df0 = df[[col]].copy()
        # remove rows that are nan for this column
        df0 = df0.dropna()
        # time interval between consecutive records
        df0['timediff'] = pd.Series(pd.to_datetime(df0.index, unit='s'), index=df0.index).diff(1).shift(-1)
        df0['timediff'] = df0['timediff'].fillna(0)
        # get the median number of steps in a 24 hr perdiod.
        steps1Day = int(pd.to_timedelta(1, unit='d') / np.median(df0['timediff']))
        # make sure it is at least 10
        if steps1Day < 10:
            steps1Day = 10

        # get the total power mean and std
        # mean total power in 24 hour period
        df0[col+'_mu'] = df0[col].rolling(steps1Day, 2).mean()
        # standard deviation
        df0[col+'_sigma'] = df0[col].rolling(steps1Day, 2).std()
        # first records get filled with first valid values of mean and standard deviation
        df0[col+'_mu'] = df0[col+'_mu'].bfill()
        df0[col+'_sigma'] = df0[col+'_sigma'].bfill()

        # if the resampled dataframe is bigger fill in new values
        if len(df0) < len(data.fixed):
            # t is the time, k is the estimated value
            t, k = estimateDistribution(df0, interval, col)  # t is number of seconds since 1970
            simulatedDf = pd.DataFrame({'time': t, 'value': k})
            simulatedDf = simulatedDf.set_index(
                pd.to_datetime(simulatedDf['time'] * 1e9))  # need to scale to nano seconds to make datanumber
            simulatedDf = simulatedDf[~simulatedDf.index.duplicated(keep='last')]
            # make sure timestamps for both df's are rounded to the same interval in order to join sucessfully
            data.fixed.index = data.fixed.index.floor(interval)
            simulatedDf.index = simulatedDf.index.floor(interval)
            # join the simulated values to the upsampled dataframe by timestamp
            data.fixed = data.fixed.join(simulatedDf, how='left')
            # fill na's for total_p with simulated values
            data.fixed.loc[pd.isnull(data.fixed['total_p']), 'total_p'] = data.fixed['value']
            # component values get calculated based on the proportion that they made up previously
            adj_m = data.fixed[data.fixed.columns[0:-1]].div(data.fixed['total_p'], axis=0)
            adj_m = adj_m.ffill()
            data.fixed = adj_m.multiply(data.fixed['total_p'], axis=0)

            # get rid of columns added
            data.fixed = data.fixed.drop('time', 1)

    data.removeAnomolies()
    return data