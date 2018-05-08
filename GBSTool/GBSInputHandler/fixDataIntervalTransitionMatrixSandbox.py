
from fixDataIntervalTransitionMatrix import fixDataIntervalTransitionMatrix
from fixDataInterval import fixDataInterval
from fixBadData import DataClass
import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt

# create a sine wave
Fs = 1/(60*15) # sampling freq: once every 15 min
t = np.arange(1000)*(60*15) # time steps every 15 min
f = 1/(60*60*24) # wave frequency: every 24 hours
values = np.sin(2 * np.pi * f * t)

raw_df = pd.DataFrame(columns=['fixed'])
raw_df.fixed.gen1 = values
raw_df.fixed.gen2 = values

# create a dataclass object
A = DataClass(raw_df, Fs)

df = fixDataInterval(A,1)

plt.plot(df)


