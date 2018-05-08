
#imports
import random


def generateTimeSeries(TM, values, startingIdx, length):
    '''
    generates a time series from a transition matrix
    :param TM: transition matrix
    :param values: a list of values associated with the transition matrix
    :param startingIdx: starting index
    :param length: number of values
    :return: time series of indicies
    '''

    ts = [values[startingIdx]] # initiate time series
    valIdx = startingIdx # the index of the value of the current step in time series
    indices = range(len(TM)) # list of possible indicies

    for idx in range(length):
        # get next index
        valIdx = random.choices(indices, weights=TM[valIdx])[0]
        # add to the time series
        ts += [values[valIdx]]

    return ts