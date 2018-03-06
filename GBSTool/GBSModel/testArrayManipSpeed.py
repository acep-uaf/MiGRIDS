# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 11:24:11 2018

@author: jbvandermeer
"""
# imports
import numpy as np
import time

# test indexing solutions

L = range(40000)

t0 = time.time()
for idx in range(1000):
    molDifference0 = [1 - x for x in L]
t1 = time.time()
print(t1-t0)

t2 = time.time()
for idx in range(1000):
    molDifference1 = 1 - np.array(L)

t3 = time.time()
print(t3-t2)