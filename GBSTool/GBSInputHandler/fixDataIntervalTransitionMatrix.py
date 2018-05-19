
def fixDataIntervalTransitionMatrix(data, interval, sigma = None, useMarkov = False, TM = [], TMvalues = [], stdNum = 3):
    '''
    changes the timesteps of a time series to a fixed interval. A transition matrix is used to upsample the data if
    the timesteps in the data are longer than the desired interval
    :param data: input time series, a DataClass object.
    :param useMarkov: Bool value whether to use Markov. Default if False. If False, Langevin will be used to upsample data.
    :param interval: desired interval in seconds
    :param TM: transition matrix of the difference from the linear difference between input data points
    :param TMvalues: the values corresponding to the TM
    :param stdNum: the number of standard deviations from mean that is acceptable in the data set. outside values trimmed off.
    :return: data with a fixed timestep
    '''

    import pandas as pd

    # df contains the non-upsampled records. Means and standard deviation come from non-upsampled data.
    df = data.fixed.copy()
    # mean
    df['mu'] = df.total_p.rolling(10, 2).mean()
    # standard deviation
    df['sigma'] = df.total_p.rolling(10, 2).std()
    # first records get filled with first valid values of mean and standard deviation
    df['mu'] = df['mu'].bfill()
    df['sigma'] = df['sigma'].bfill()
    # time interval between consecutive records
    df['timediff'] = pd.Series(pd.to_datetime(df.index, unit='s'), index=df.index).diff(1).shift(-1)
    df['timediff'] = df['timediff'].fillna(0)

    # up or down sample to our desired interval
    # down sampling results in averaged values
    data.fixed = data.fixed.resample(pd.to_timedelta(interval)).mean()

    # integer, numeric, numeric, numeric -> numeric array
    # uses the Langevin equation to estimate records based on provided mean (mu) and standard deviation and a start value
    def getValues(records, start, sigma, timestep):
        import numpy as np

        # number of steps
        n = (records / timestep) + 1
        # time constant. This value was empirically determined to result in a mean value between
        tau = records * .2

        # renormalized variables
        # TODO: look at sigma calculation
        sigma_bis = sigma * np.sqrt(2.0 / n)  # adapted from ipython interactive computing visualization cookbook
        sqrtdt = np.sqrt(timestep)
        # x is the array that will contain the new values
        x = np.zeros(shape=(len(start), int(max(n))))
        # the starter value
        x[:, 0] = start
        # use the next step in the time series as the average value for the synthesized data. The values will asympotically reach this value, resulting in a smooth transition.
        mu = start.shift(-1)
        mu.iloc[-1] = mu.iloc[-2]

        for i in range(int(max(n) - 1)):
            x[:, i + 1] = x[:, i] + timestep * (-(x[:, i] - mu) / tau) + np.multiply(sigma_bis.values * sqrtdt,
                                                                                     np.random.randn(len(mu)))

        return x

    def getValuesMarkov(records, start, timestep, TM, TMvalues):
        '''
        calculates values based on markov chain
        :param records:
        :param start:
        :param mu:
        :param sigma:
        :param timestep:
        :param TM:
        :return:
        '''
        import numpy as np
        from GBSAnalyzer.CurveAssemblers.generateTimeSeriesFromTransitionMatrix import generateTimeSeries
        # number of steps
        n = [int(x) for x in ((records / timestep) + 1)]

        # x is the array that will contain the new values
        x = np.zeros(shape=(len(start), int(max(n))))
        thisStep = 0 # keeps track of the current timestep
        startingIdx = np.searchsorted(TMvalues, 0, side='left') # initial difference is zero
        for ii in range(len(start)): # for each original value
            # add linear spaced values to the differences to get total values
            x[ii,:n[ii]] = generateTimeSeries(TM, TMvalues, startingIdx, n[ii]) + np.linspace(start[ii],start[np.min([ii+1,len(start)-1])],n[ii])


        return x

    # dataframe -> integer array, integer array
    # returns arrays of time as seconds and values estimated using the Langevin equation
    # for all gaps of data within a dataframe
    def estimateDistribution(df, interval, sigma = None, useMarkov = False, TM = [], TMvalues = []):
        import numpy as np
        # feeders for the langevin estimate
        mu = df['mu']
        start = df['total_p']
        if sigma is None:
            sigma = df['sigma']
        records = df['timediff'] / pd.to_timedelta(interval)
        timestep = pd.Timedelta(interval).seconds

        # return an array of arrays of values
        if not useMarkov:
            y = getValues(records, start, sigma, timestep)
        else:
            y = getValuesMarkov(records, start, timestep, TM, TMvalues)

        # steps is an array of timesteps in seconds with length = max(records)
        steps = np.arange(0, max(records) + 1, timestep)

        # t is the numeric value of the dataframe timestamps
        t = pd.to_timedelta(pd.Series(pd.to_datetime(df.index.values, unit='s'), index=df.index)).dt.total_seconds()
        # test if the index can be interpreted as datetime, if not recognized, convert
        # try:
        #    t = pd.to_timedelta(pd.Series(df.index.values)).dt.total_seconds()
        # except ValueError:
        #    t = pd.to_timedelta(pd.Series(pd.to_datetime(df.index.values, unit='s'), index=df.index)).dt.total_seconds()
        # intervals is the steps array repeated for every row of time
        intervals = np.repeat(steps, len(t), axis=0)
        # reshape the interval matrix so each row has every timestep
        intervals_reshaped = intervals.reshape(len(steps), len(t))
        tr = t.repeat(len(steps))
        rs = tr.reshape(len(t), len(steps))
        time_matrix = rs + intervals_reshaped.transpose()
        # put all the times in a single array
        timeArray = np.concatenate(time_matrix)
        # put all the values in a single array
        values = np.concatenate(y)

        return timeArray, values

    # if the resampled dataframe is bigger fill in new values
    if len(df) < len(data.fixed):
        # t is the time, k is the estimated value
        t, k = estimateDistribution(df, interval, sigma, useMarkov, TM , TMvalues )  # t is number of seconds since 1970
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

    data.removeAnomolies(stdNum = stdNum)
    return data
