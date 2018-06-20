
import pandas as pd
import numpy as np

def avg_datetime(series):
    dt_min = series.min()
    deltas = [x-dt_min for x in series]
    return dt_min + (series - dt_min).mean()

def adjustColumnYear(df):

    # get mean non-nan date of each column
    meanDate = []
    for idx, col in enumerate(df.columns):
        meanDate = meanDate + [avg_datetime(df.index.date[df[col].notnull()])]

    # get the overall mean date
    meanDateOverall = avg_datetime(pd.Series(meanDate))

    # if difference from overall mean date is more than one year, scale by closest number of years

    for idx, col in enumerate(df.columns):
        yearDiff = np.round((meanDate[idx] - meanDateOverall).days / 365)
        # if the difference is greater than a year
        if np.abs(yearDiff) > 0:
            df0 = df[[col]].copy()
            df0.dropna()
            df0.index = df0.index - pd.to_timedelta(yearDiff, unit='y')
            df.drop(col,axis=1,inplace=True)
            df = pd.concat([df, df0], axis=1)
            df.dropna(how = 'all',inplace=True)

    return df