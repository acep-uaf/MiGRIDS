#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 22:47:37 2018

@author: marcmueller-stoffels
"""

import time
import numpy as np

itNum = 100000

'''
ll = 11

tl = list(range(0,ll))

st = time.time()

for i in range(0,ll):
    m = np.nanmax(tl)

nm_t = time.time() - st
print('np.nanmax() takes %s seconds.' % str(nm_t))

tl = list(range(0,ll))

st = time.time()

for i in range(0,ll):
    m = max(tl)

m_t = time.time() - st
print('Max() takes %s seconds.' % str(m_t))

print('Max takes %s percent of np.max()' % str(100*m_t/nm_t))
'''

#**************** NANMAX ***********************************

st = time.time()

a = 0
b = 0
for j in range(0,itNum):
    b = np.sum(b)
    if b == 0:
        c = 0
    else:
        c = max([a/sum(b), 0])

if_t = time.time() - st

print('Checking for division by 0 takes %s seconds.' % str(if_t))

st = time.time()

a = 0
b = 0
for j in range(0,itNum):
    c = np.nanmax([a/np.sum(b),0])

nan_t = time.time() - st

print('Checking for nan in max takes %s seconds.' % str(nan_t))

print('Div by 0 check duration is %s percent of nanmax check.' % str(round(100*if_t/nan_t)))
