
from fixDataIntervalTransitionMatrix import fixDataIntervalTransitionMatrix
from fixDataInterval import fixDataInterval
from fixBadData import DataClass
import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
import datetime

# create a sine wave
Fs = 1/(60*15) # sampling freq: once every 15 min
t = np.arange(1000)*(60*15) # time steps every 15 min
f = 1/(60*60*24) # wave frequency: every 24 hours
values = np.sin(2 * np.pi * f * t)*100

# datetime
base = pd.datetime.today()
date_list = pd.to_datetime([base + pd.Timedelta(minutes=x*15) for x in range(0, 1000)])

# add some gaussian noise
for idx in range(1000):
    values[idx] += random.gauss(30,10) - 15

raw_df = pd.DataFrame({'date': date_list, 'gen1': values, 'gen2':values},index=date_list)

# create a dataclass object
A = DataClass(raw_df, Fs)
A.powerComponents = ['gen1','gen2']
A.totalPower()
df = fixDataInterval(A,'1s')

plt.plot(df.fixed.gen1,'*-')
plt.plot(df.raw.gen1,'*-')
plt.show()


