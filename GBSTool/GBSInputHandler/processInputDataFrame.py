# general imports
import numpy as np
import pandas as pd
from GBSInputHandler.convertDateTimeFormat import convertDateTimeFormat
import pytz


def processInputDataFrame(inputDict):
    try:
        # find Date column
        # convert the date to datetime
        # TODO this is taking a very long time to run - several hours for 1 year long file
        df = inputDict['df']
        if inputDict['dateColumnFormat'] == 'infer':
            df['DATE'] = df[inputDict['dateColumnName']].apply(pd.to_datetime,infer_datetime_format=True, errors='coerce')
            # remove rows that did not work
            df = df.drop(df.index[pd.isnull(df['DATE'])])
        else:
            df['DATE'] = df[inputDict['dateColumnName']].apply(lambda d: pd.to_datetime(d,format=convertDateTimeFormat(inputDict['dateColumnFormat']),errors='coerce') )

        # add time to date, if there is a time column. if not, timeColumnFormat should be ''
        #if timeColumnFormat == 'infer':
        df['DATE'] = df['DATE'] + df[inputDict['timeColumnName']].apply(pd.to_timedelta, errors='coerce')
        # remove rows that did not work
        df = df.drop(df.index[pd.isnull(df['DATE'])])
        #else:
            #df['DATE'] = df['DATE'] + df[timeColumnName].apply(lambda t: pd.to_datetime(t,format=convertDateTimeFormat(timeColumnFormat)))

        # convert data columns to numeric
        for idx, col in enumerate(inputDict['columnNames']):
            try:
                df[col] = df[col].apply(pd.to_numeric, errors='coerce')
            except:
                df[col] = df[col.replace('_',' ')].apply(pd.to_numeric, errors='coerce')
            # change col name to the desired name
            df = df.rename(columns={col:inputDict['useNames'][idx]})

        # remove other columns
        if isinstance(inputDict['useNames'], (list, tuple, np.ndarray)):  # check if multple collumns
            #if date was inferred we have a DATE column otherwise we don't
            if inputDict['dateColumnFormat'] == 'infer':
                df = df[['DATE'] + inputDict['useNames']]  # combine date and time with columns to keep
        else:
            df = df[['DATE'] + [inputDict['useNames']]]  # combine date and time with columns to keep

        # convert to utc time
        df = dstFix(df,inputDict['timeZone'],inputDict['dst'])

        # order by datetime
        df = df.sort_values(['DATE']).reset_index(drop=True)
        return df
    except KeyError as k:
        print('The required key %s was not included in the input dictionary' %k)
        return

def dstFix(df,timeZone,useDST):
    try:
        timeZone = pytz.timezone(timeZone)
        df['DATE']=df['DATE'].apply(lambda d: timeZone.localize(d,is_dst=useDST))
        df['DATE']=df['DATE'].dt.tz_convert('UTC')
    except Exception as e:
        print(str(e))
        print(type(e))

    return df
