#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 13:20:26 2018

@author: marcmueller-stoffels
"""

import time

iterNum = 100000
ll = 100
bl = [False] * ll
bl[50] = True

st = time.time()

for i in range(0, iterNum):
    if True in bl:
        a = 1

et = time.time()
t0 = et-st
print(t0)


st = time.time()

for i in range(0, iterNum):
    if any(bl):
        a = 1

et = time.time()
t1 = et-st
print(t1)
print(100*t0/t1)