#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 15:57:43 2018

@author: marcmueller-stoffels
"""

import time
import numpy as np

iters = 1000000#365*24*60*60

ts = time.time()
ll = 3

tl = list(range(0,ll))
print(type(tl))

for i in range(0,iters):
    s = sum(tl)

t_l_sum = time.time() - ts

ts = time.time()
ll = 3

tl = list(range(0,ll))
print(type(tl))

for i in range(0,iters):
    s = np.sum(tl)

t_l_npsum = time.time() - ts

ts = time.time()

tl = np.arange(0,ll)
print(type(tl))

for i in range(0,iters):
    s = sum(tl)

t_na_sum = time.time() - ts

ts = time.time()

tl = np.arange(0,ll)
print(type(tl))

for i in range(0,iters):
    s = np.sum(tl)

t_na_npsum = time.time() - ts

print('List and sum: ' + str(t_l_sum) + ' seconds.')
print('List and np.sum: ' + str(t_l_npsum) + ' seconds.' )
print('Array and sum: ' + str(t_na_sum) + ' seconds.')
print('Array and np.sum: ' + str(t_na_npsum) + ' seconds.')