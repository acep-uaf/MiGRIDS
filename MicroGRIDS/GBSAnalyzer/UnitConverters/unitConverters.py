# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: September 30, 2017 -->
# License: MIT License (see LICENSE file of this package for more information)

# This file contains an assembly of functions used for unit conversion. The method name corresponds directly with the
# conversion, e.g., gallons2liter converts US gallons to liters.


def gal2l(gallon):
    """
    Converts US gallons to liters using the conversion:

        1 US gallon = 3.78541 l

    :param gallon: US gallons to convert
    :return liter: the US gallons converted to liters
    """

    liter = 3.78541 * gallon
    return liter

# Liters to gallons
# Converts liters to US liquid gallons using the conversion:
#   $$
#       1 liter  = 0.264172 gallons
#   $$
def l2gal(liter):
    gallon = 0.264172 * liter
    return gallon

# Liters to cubic meters
# Converts liters to cubic meters using the conversion:
#   $$
#       1 l = 0.001 m^3
#   $$
def l2cubicMeter(liter):
    cubicMeter = 0.001 * liter
    return cubicMeter

# Watts to kW
# Converts watts to kW using the conversion:
#   $$
#       1 kW = 1000 W
#   $$
def w2kw(w):
    kw = 1000 * w
    return kw

# MW to kW
# Converts MW to kW the conversion:
#   $$
#       1 MW = 0.001 kW
#   $$
def mw2kw(mw):
    kw = 0.001 * mw
    return kw

# Celcius to Kelvin
# Converts degrees C to degrees K using the following conversion:
#   $$
#       1 K = C + 273.15
#   $$
def c2k(c):
    k = c + 273.15
    return k

# Fahrenheit to Kelvin
# Converts degrees F to degrees K using the following conversion:
#   $$
#       1 K = (K + 459.67)*(5/9)
#   $$
def f2k(f):
    k = (f+459.67)*(5/9)
    return k

def lph2kgps(lph):
    """
    Volume to mass flow converter Liters/hour to kg/s.

    This converter works for **diesel fuel at room temperature only**. Do not use for any other liquids without
    adjusting the conversion factor.

    The conversion is 1 kg/s = 0.875/3600 l/h.

    :param lph: liter per hour volume flow input
    :return kgps: kg per second mass flow output
    """

    kgps = (0.875/3600) * lph
    return kgps

