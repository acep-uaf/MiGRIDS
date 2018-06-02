
def processInputDataFrame(df, columnNames, useNames, dateColumnName, dateColumnFormat, timeColumnName = '', timeColumnFormat = '', utcOffsetValue = None, utcOffsetUnit = None, dst = None):
    # general imports
    import numpy as np
    import pandas as pd

    # find Date column
    # convert the date to datetime
    if dateColumnFormat == 'infer':
        df['DATE'] = df[dateColumnName].apply(pd.to_datetime,infer_datetime_format=True, errors='coerce')
        # remove rows that did not work
        df = df.drop(df.index[pd.isnull(df['DATE'])])

    # add time to date, if there is a time column. if not, timeColumnFormat should be ''
    if timeColumnFormat == 'infer':
        df['DATE'] = df['DATE'] + df[timeColumnName].apply(pd.to_timedelta, errors='coerce')
        # remove rows that did not work
        df = df.drop(df.index[pd.isnull(df['DATE'])])

    # convert data columns to numeric
    for idx, col in enumerate(columnNames):
        df[col] = df[col].apply(pd.to_numeric, errors='coerce')
        # change col name to the desired name
        df = df.rename(columns={col:useNames[idx]})

    # remove other columns
    if isinstance(useNames, (list, tuple, np.ndarray)):  # check if multple collumns
        df = df[['DATE'] + useNames]  # combine date and time with columns to keep
    else:
        df = df[['DATE'] + [useNames]]  # combine date and time with columns to keep

    # convert to utc time
    df['DATE'] = df['DATE'] - pd.to_timedelta(utcOffsetValue + utcOffsetUnit)
    #
    # TODO: we will need to deal with daylight savings
    # convert to int64 convert to Unix time
    index = pd.DatetimeIndex(df.DATE)
    df.DATE = index.astype(np.int64)//10**9 # convert from microseconds to seconds since base time

    # order by datetime
    df = df.sort_values(['DATE']).reset_index(drop=True)

    return df