# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: March 3, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import numpy as np

# calculate the minimum required src

def getMinSrc(wtgPimport, prevLoad, timeStep):
    # Take the average load of this hour last week 24.5hr * 3600 s/hr = 617400s , 23.5hr * 3600 = 592200
    # try with and without, compare the difference in performance.
    #meanLastWeek = np.mean(prevLoad[int(-617400/timeStep):int(-592200/timeStep)])
    # if a list is given for prevLoad, get mean value, otherwise, use the value given
    if type(prevLoad) is list or type(prevLoad) is np.ndarray:
        meanLastTenMin = np.mean(prevLoad[int(-600/timeStep):])
    else:
        meanLastTenMin = prevLoad
    return meanLastTenMin*0.25 + wtgPimport*.75