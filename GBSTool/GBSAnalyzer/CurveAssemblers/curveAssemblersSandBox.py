# Just a little test harness for the routines in this subpackage.
from wtgPowerCurveAssembler import WindPowerCurve
import matplotlib.pyplot as plt
from sys import getsizeof
import numpy as np

pwrCrv = WindPowerCurve()
pwrCrv.powerCurveDataPoints = [(1, 0), (2, 0), (3, 0), (4, 3.7), (5, 10.5),
(6, 19.0), (7, 29.4), (8, 41.0), (9, 54.3), (10, 66.8), (11, 77.7), (12, 86.4), (13, 92.8), (14, 97.3),
(15, 100.0), (16, 100.8), (17, 100.6), (18, 99.8), (19, 99.4), (20, 98.6), (21, 97.8), (22, 97.3),
(23, 97.3), (24, 98.0), (25, 99.7)]
pwrCrv.cutInWindSpeed = 3.5
pwrCrv.cutOutWindSpeedMin = 3.49
pwrCrv.cutOutWindSpeedMax = 26
pwrCrv.POutMaxPa = 100.9

pwrCrv.cubicSplineCurveEstimator()
pc = pwrCrv.powerCurve
pcInt = pwrCrv.powerCurveInt
print(getsizeof(pc))
print(getsizeof(pcInt))
plt.figure(figsize=(6.5, 4))
x, y = zip(*pwrCrv.powerCurveDataPoints)
plt.plot(x,y,'o')
xCs, yCs = zip(*pwrCrv.powerCurve)
plt.plot(xCs, yCs, '.')
plt.show()

print(np.max(np.diff(yCs, 1), 0))
