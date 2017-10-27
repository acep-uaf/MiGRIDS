# Just a little test harness for the routines in this subpackage.
from wtgPowerCurveAssembler import WindPowerCurve

pwrCrv = WindPowerCurve()
pwrCrv.powerCurveDataPoints = [(1, 1), (1,1)]
pwrCrv.cutInWindSpeed = 1
pwrCrv.cutOutWindSpeedMin = 0.5
pwrCrv.cutOutWindSpeedMax = 25
pwrCrv.POutMaxPa = 100

pwrCrv.cubicSplineCurveEstimator()
