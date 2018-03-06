# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 1, 2018
# License: MIT License (see LICENSE file of this package for more information)

# get the index of an interger value in a list of continuous sequential intergers
# using integer list indexing is much faster than np.searchsorted
# List is an interger list, with no missing values, with stepsize intervals between values
# value is the value being searched for
# stepsize is the size of the step between values in List
def getIntListIndex(value, List, stepsize = 1):
    valueInt = int(value/stepsize)*stepsize # convert to interger
    if valueInt < List[0]: # if below range, assigne first value
        idx = 0
    elif valueInt > List[-1]: # if above range, assigne last value
        idx = len(List)-1
    else: # otherwise, find index
        idx = List.index(valueInt)
    return idx
