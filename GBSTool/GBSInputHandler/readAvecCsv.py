# TODO: File header here
# TODO: Use more comments throughout ;-)
# TODO: Bundle all `import' statements at the top

print('Hello World')

# cd to the Resources dir to get input files
# TODO: Set this up such that it can easily setup with an interactive interface later (either command line or GUI)
import os
print(os.getcwd())
dir = os.path.dirname(__file__)
newdir = os.path.join(dir,'..\..\InputData\Chevak')
os.chdir(newdir)
import os
print(os.getcwd())

# load csv file
# TODO: While the import ... with ... definitely works this way, this also hard codes the file you are opening, which is not desirable.
import csv
with open('ChevakDispatch201612.csv','r') as csvfile:
    reader = csv.reader(csvfile,delimiter = ',')
    data = list(reader)
    #for row in data:
     #   print(', '.join(row))

print(data[3])

# TODO: yupp, pandas should do all the tricks we need it to do...
import pandas as pd
df = pd.read_csv('ChevakDispatch201612.csv')

import numpy as np
x=np.array(df)
x
y=x.astype(np.float) # cannot convert string to float

# TODO: have you already found a good cheat sheet for regular expressions? Let me know if you need one.
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
