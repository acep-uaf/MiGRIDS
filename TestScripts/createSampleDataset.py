import pandas as pd
import os
import numpy as np
from collections import OrderedDict
from scipy.stats import bernoulli
from pandas.tseries.offsets import MonthEnd

def createLoad(d1,d2,f):
    
   
    loadOffset = np.random.randint(low=1, high=10)
    loadStart = d1 + pd.Timedelta(seconds=loadOffset)
    loadIndex = pd.date_range(start=loadStart, end=d2, freq=f)  # 4320
    loadAdjust = np.random.randint(low=0, high=5, size=len(loadIndex))
    
    probAdjust = pd.Series(loadIndex.to_datetime()).apply(lambda d: createTimeProbs(d))
   
    loadAdjust = loadAdjust * probAdjust  
    
    loadData = fillData( np.random.randint(low=200,high=300, size = 1),loadAdjust)
    
    df = pd.DataFrame(loadData)
    
    df.index = loadIndex

    return df

def fillData(startValue,adjusters):
    adjusters[0] = adjusters[0] + startValue
    for i in range(1,len(adjusters[1:])):
        adjusters[i] = adjusters[i-1] + adjusters[i]
    
    return adjusters   
     
def createHighResLoad(d1,d2):
    df =createLoad(d1,d2,'10 min')
    df.columns = ['Villagekw']
    return df
    
def createLowResLoad(d1, d2):
    df =createLoad(d1,d2,'30 min')
    df.columns = ['loadkw']
    return df

def createTimeProbs(dt):
    def b_to_neg(x):
        
        if x == 2:
            return 1
        elif x == 1:
            return -1
        else:
            return x
    
    if dt.hour <= 4:
        #prob of increasing = 0
        return b_to_neg(bernoulli.rvs(0.5,1))   
    elif (dt.hour > 4) & (dt.hour < 7):
        return b_to_neg(bernoulli.rvs(0.8,1))
    elif (dt.hour >= 7) & (dt.hour < 17):
        return b_to_neg(bernoulli.rvs(0.5,1))
    elif (dt.hour >= 17) & (dt.hour < 19):
        return b_to_neg(bernoulli.rvs(0.3,1))  
    elif (dt.hour >= 19) & (dt.hour < 23):
        return b_to_neg(bernoulli.rvs(0.1,1))
    elif (dt.hour >= 23):
        return b_to_neg(bernoulli.rvs(0.5,1))

def writeDataFrames(lod,lof):
    for i, df in enumerate(lod):
        fileName = df.index[0].strftime("%m%d%Y%H%M") + df.index[len(df)-1].strftime("%m%d%Y%H%M") +".csv"
        if not os.path.exists(lof[i]):
            os.makedirs(lof[i])
        df.to_csv(os.path.join(lof[i],fileName),
                  sep=",",
                  header=True,
                  index=True, 
                  index_label = 'DATE')
    return

def toProject(baseDir,folders):
    folderList = [os.path.join(baseDir,*['InputData','TimeSeriesData','RawData', x]) for x in folders]
    return folderList

def makeHeader():
    header = """0.0.0\n \n -----Logger Information-----\n\n
Model #	xxxx
Serial #	xxxxx
Hardware Rev.	011-010-000

-----Site Information-----
Site #	0000
Site Desc	xx
Project Code	xx
Project Desc	xx
Site Location	xx
Site Elevation	800
Latitude	N 00° 00.000'
Longitude	W 100° 00.000'
Time offset (hrs)	-9')

-----Sensor Information-----

Channel #	1
Type	1
Description	NRG IceFreeIII m/s
Details	
Serial Number	SN:
Height	 40   m
Scale Factor	0.572
Offset 	0.35
Units	m/s

Channel #	2
Type	1
Description	NRG IceFreeIII m/s
Details	
Serial Number	SN:
Height	 18   m
Scale Factor	0.652
Offset	 1
Units	m/s

Channel #	3
Type	1
Description	NRG IceFreeIII m/s
Details	
Serial Number	SN:
Height	30   m
Scale Factor	1
Offset	 0.1
Units	m/s

Channel #	4
Type	1
Description	NRG IceFreeIII m/s
Details	
Serial Number	SN:
Height	21   m
Scale Factor	0.784
Offset 	0.1
Units	m/s


"""

    return header
def makeMETdf(d1):
    timerange = pd.date_range(start=d1,end=d1 + MonthEnd(1),freq='30 min')
    df = pd.DataFrame({'Date & Time Stamp': timerange}) #'Date & Time Stamp'
    for c in [1,2,3,4]:
        channel = 'CH' + str(c)
        avg = channel + 'Avg'
        sd = channel + 'SD'
        min_ = channel + 'Min'
        max_ = channel + 'Max'
        
    
        windAvg = np.random.randint(low = 0, high = 15, size=len(timerange))
        windSd = np.random.randint(low = 2, high = 15, size=len(timerange))
        windSd = windSd/10
        windMin = windAvg - (3 * windSd)
        windMin[windMin < 0] = 0
        windMax = windAvg + (3 * windSd)
        
        df = df.join(pd.DataFrame(OrderedDict({
                           avg:windAvg,
                           sd:windSd,
                           min_:windMin,
                           max_:windMax})), how='right')
    
    return df

def createMET(d1,d2):
    import re
    header = makeHeader()
    months = pd.date_range(start=d1,end=d2,freq='MS')
    months = [d1.strftime("%Y-%m-%d %H:%M:%S")] + months.strftime("%Y-%m-%d %H:%M:%S").tolist() + [d2.strftime("%Y-%m-%d %H:%M:%S")]
    text = []
    for i,d in enumerate(months):
        df = makeMETdf(pd.to_datetime(d))
        
        text.append( header + "\n\n" + re.sub('  +', '\t',df.to_string(header=True,index = False)))
       
    return text
    
def writeMET(d,filename):
    with open(filename, encoding='utf-8', mode='w') as file:
        #file.writelines(d)
        file.write(d)
    return

def main():
    projectDir = os.path.join(os.getcwd(),*["..","MicroGRIDSProjects","SampleProject"])
    startD = pd.to_datetime('11/15/2007')
    endD = pd.to_datetime('02/15/2008')
    dfh1 = createHighResLoad(pd.to_datetime('11/15/2007'), pd.to_datetime('12/15/2007'))
    dfh2 = createHighResLoad(pd.to_datetime('12/15/2007'), pd.to_datetime('01/15/2008'))
    dfh3 = createHighResLoad(pd.to_datetime('01/15/2008'), pd.to_datetime('02/15/2008'))
    
    dfl = createLowResLoad(startD, endD)
    
    writeDataFrames([dfh1,dfh2,dfh3,dfl,],
                    toProject(projectDir,['HighRes','HighRes','HighRes','LowRes']))
    met = createMET(startD,endD)
    if not os.path.exists(os.path.join(projectDir,'InputData','TimeSeriesData','RawData','RawWind')):
        os.makedirs(os.path.join(projectDir,'InputData','TimeSeriesData','RawData','RawWind'))
    
    for i,m in enumerate(met):
        
        writeMET(m, os.path.join(projectDir,'InputData','TimeSeriesData','RawData','RawWind', 'met{0}.txt'.format(i)))
    

if __name__ == '__main__':
    main()