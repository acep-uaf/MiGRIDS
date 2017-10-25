# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def fixDataInterval(df,interval):
    # df is the pandas dataframe, where the first column is a dateTime column
    # interval is the desired interval of data samples. If this is significantly less than what is available in the df
    # (or for section of the df with missing measurements) upsampling methods will be used.

    # temporary fix

    # df_fixed is the fixed data (replaced bad data with approximated good data)
    df_fixed = df


    return df_fixed

