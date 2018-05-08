# series -> series
# returns the group id for values in the series, consecutive values will belong to the same group
def isInline(x):
    grouping = x.diff().ne(0).cumsum()
    return grouping
