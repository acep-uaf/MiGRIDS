# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc.mueller.stoffels@gmail.com
# Date: September 30, 2017 -->
# License: MIT License (see LICENSE file of this package for more information

# This function will eventually return a functional estimate for the power curve of a wind turbine based on data provided
# in 'wtgDescriptor.xml'.
# Currently this is only a place holder since the script was mentioned in documentation.

'''
TODO: Define and implement power curve assembler.

OBJECTIVE: The fuctionality of this class is to:
    a) determine if the data provide in wtgDescriptor.xml already is sufficiently dense to define the power curve without
    estimation of additional points.
    b) if necessary estimate additional points of the power curve such that a dense curve available.

A dense curve will have power levels associated with all wind speeds in increments of 0.1 m/s and approximates power in
1 kW steps.

ASSUMPTIONS:
    INPUTS: data used as input is already from a cleaned up power curve. This tool is not intended to produce a power
    from operational time-series data, which would require cleaning and filtering. Thus, it is required that for each
    wind speed value one and only one power value exists. That is, temperature compensations, if desired will have to be
    handled separately.
    
'''