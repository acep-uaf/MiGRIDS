#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 10:42:44 2018

@author: marcmueller-stoffels
"""

import pandas as pd
import time
import numpy as np

genCombsP = [0, 135, 225, 315, 360, 450, 540, 675.0]
loadings = list(range(0, int(max(genCombsP)+1)))
indCapAll = np.array(range(0,len(genCombsP)))
maxIndCap = np.max(indCapAll)

# Set up some test loads
randLoadsLen = 1000000
randLoadsNP = 700 * np.random.random(randLoadsLen)
randLoads = [None]*randLoadsLen
for idz, rlnp in enumerate(randLoadsNP):
    randLoads[idz] = float(rlnp)

# LOOK UP TABLE TEST
#st_lkp = time.time()
#
#lookUpTab = pd.DataFrame(False, index=loadings, columns = list(range(0,len(genCombsP))))
#
#for idx in lookUpTab.index:
#    for idy, genComb in enumerate(genCombsP):
#        if idx <= genComb:
#            lookUpTab[idy].loc[idx] = True
#
#
#for randLoad in randLoads:
#    # Look up
#    indCap = indCapAll[lookUpTab.loc[int(randLoad)]]
#
#et_lkp = time.time()
#
#print('Look up table method time elapsed : ' + str(et_lkp - st_lkp) + ' seconds.')

# Inline loop code test
st_ilp = time.time()

for randLoad in randLoads:
    indCap = np.array([idx for idx, x in enumerate(genCombsP) if x >= randLoad])
    
et_ilp = time.time()

print('Inline loop method time elapsed : ' + str(et_ilp - st_ilp) + ' seconds.') 

# DICTIONARY
st_dict = time.time()

lkpDict = {}

for load in loadings:
    combList = np.array([])
    for idy, genComb in enumerate(genCombsP):
        if load <= genComb:
            np.append(combList, idy)
    lkpDict[load] = combList

for randLoad in randLoads:
    indCap = lkpDict.get(int(randLoad), maxIndCap)

et_dict = time.time()
    
print('Dict look up method time elapsed : ' + str(et_dict - st_dict) + ' seconds.') 