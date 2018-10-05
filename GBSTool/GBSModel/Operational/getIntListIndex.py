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




def getIntDictKey(value, valDict, minKeyInDict, maxKeyInDict, stepsize = 1):
    '''
    Index lookup from continuous sequential dictionary of integers. In order to use something like the List variable that
    is the input to getIntListIndex the following conversion (performed outside of loops) can be used
    valDict = dict(zip(List, range(len(List))). It is also useful to precalculate the min and max value in the Dict
    (technically the min and max key) at that time to avoid repeated calls to min and max functions, which is costly, as
    this function is most often called in a loop across a time-series.

    :param value: [float] value to find the index for
    :param valDict: [dict] integer values for which an index is to be looked up for are the keys to this dict. Indices
        are returned by valDict[valueInt].
    :param minValInDict: [int] minimum key in the dictionary. If the input value is lower, the default key assigned is 0
    :param maxValInDict: [int] maximum key in the dictionary. If the input value is higher, the default key assigned is largest available.
    :param stepsize: [float] the size of the step between keys in dictionary
    :return idx: an integer value corresponding to the key in the input dictionary, associated with the looked up value
    '''
    valueInt = int(value / stepsize) * stepsize  # convert to interger
    maxIdx = len(valDict) - 1
    if valueInt < minKeyInDict:  # if below range, assigne first value
        idx = 0
    elif valueInt > maxKeyInDict:  # if above range, assigne last value
        idx = maxIdx
    else:  # otherwise, find index
        idx = valDict[valueInt]
    return idx