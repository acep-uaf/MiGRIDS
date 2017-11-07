# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc.mueller.stoffels@gmail.com
# Date: September 30, 2017 -->
# License: MIT License (see LICENSE file of this package for more information)

# This file contains an assembly of functions used for unit conversion. The method name corresponds directly with the
# conversion, e.g., gallons2liter converts US gallons to liters.

"""
General Notes

EMPTY
"""


# Gallons to liters
# Converts US gallons to liters using the conversion:
#    $$
#        1 US gallon = 3.78541 l
#    $$
def gallon2liter(gallon):
    liter = 3.78541 * gallon
    return liter

# Liters to gallons
# Converts liters to US liquid gallons using the conversion:
#   $$
#       1 liter  = 0.264172 gallons
#   $$
def liter2gallon(liter):
    gallon = 0.264172 * liter
    return gallon

# Liters to cubic meters
# Converts liters to cubic meters using the conversion:
#   $$
#       1 l = 0.001 m^3
#   $$
def liter2cubicMeter(liter):
    cubicMeter = 0.001 * liter
    return cubicMeter

