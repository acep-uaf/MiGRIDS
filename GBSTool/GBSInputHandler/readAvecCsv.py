print('Hello World')

# cd to the Resources dir to get input files
import os
print(os.getcwd())
dir = os.path.dirname(__file__)
newdir = os.path.join(dir,'..\..\InputData\Chevak')
os.chdir(newdir)
import os
print(os.getcwd())
# load csv file
import csv
with open('ChevakDispatch201612.csv','r') as csvfile:
    reader = csv.reader(csvfile,delimiter = ',')
    data = list(reader)
    #for row in data:
     #   print(', '.join(row))

print(data[3])

import pandas as pd
df = pd.read_csv('ChevakDispatch201612.csv')

import numpy as np
x=np.array(df)
x
y=x.astype(np.float) # cannot convert string to float

import re
non_decimal = re.compile(r'[^\d.]+')
non_decimal.sub('', '12.345i5ii3')

import math
for i in range(x.shape[0]):
    for j in range(x.shape[1]):
        if isinstance(x[i,j],str): #if is string
            a = non_decimal.sub('', x[i, j]) # remove all non-numeric values from string
            try:
                x[i,j] = float(a)
            except:
                x[i,j] = []
        #if math.isnan(x[i,j]):
            #x[i,j]=[]
