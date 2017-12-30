# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

#Reads a dataframe and ouputs a new dataframe with the specified sampling time interval.
#If interval is less than the interval within the dataframe mean values are used to create a down-sampled dataframe
#If interval is greater than the interval within a dataframe linear interpolation is used to up-sample the dataframe
#Dataframe, String -> dataframe
def fixDataInterval(df,interval):
    # df is the pandas dataframe, where the first column is a dateTime column
    # interval is the desired interval of data samples. If this is significantly less than what is available in the df
    # (or for section of the df with missing measurements) upsampling methods will be used.
    import pandas as pd
    time_index = pd.to_datetime(df.iloc[:,0])
    resample_df = pd.DataFrame(df.copy())
    resample_df.index = time_index
    resample_df = resample_df.resample(interval).mean().interpolate()
    return resample_df
    

        
    
        


