import os
import pickle
from GBSInputHandler.adjustColumnYear import adjustColumnYear
import matplotlib.pyplot as plt

setupDir = 'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools_0\GBSProjects\StMary\InputData\Setup'
os.chdir(setupDir)
os.chdir('../TimeSeriesData/RawData')
inFile = open("raw_df.pkl","rb")
df = pickle.load(open("raw_df.pkl","rb"))
inFile.close()

df0 = adjustColumnYear(df)

plt.plot(df0.load0P)
plt.plot(df0.load1P)