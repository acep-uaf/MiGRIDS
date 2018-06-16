
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
        meanDate = meanDate + avg_datetime(df.index.iloc[df[col] is not None])

    # get the overall mean date
    meanDateOverall = np.mean(meanDate)

    # if difference from overall mean date is more than one year, scale by closest number of years

    for idx, col in enumerate(df.columns):
        yearDiff = np.round((meanDate[idx] - meanDateOverall).days / 365)
        # if the difference is greater than a year
        if np.abs(yearDiff) > 0:
            df0 = df[[col]].copy()
            df0.dropna()
            df0.index = df0.index + pd.to_timedelta(yearDiff, unit='y')
            df[col] = df0


    # check if on average more than a year difference between new dataset and existing
    meanTimeNew = avg_datetime(df0.DATE)
    meanTimeOld = avg_datetime(df.DATE)
    # round to the nearest number of year difference

    # if the difference is greater than a year between datasets to be merged, see if can change the year on one
    if abs(yearDiff) > 0:
        # if can change the year on the new data
        if inputDictionary['flexibleYear'][idx]:
            # find the number of years to add or subtract
            df0.DATE = df0.DATE - pd.to_timedelta(yearDiff, unit='y')
        # otherwise, check if can adjust the existing dataframe
        elif all(inputDictionary['flexibleYear'][:idx]):
            df.DATE = df.DATE + pd.to_timedelta(yearDiff, unit='y')
