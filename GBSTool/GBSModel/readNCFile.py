# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: February 13, 2018
# License: MIT License (see LICENSE file of this package for more information)


from netCDF4 import Dataset
import numpy as np

# reads a net cdf file that has variables time and value, where value has the attributes scale, offset and units and time
# has the attribute units.
class readNCFile:


    def __init__(self, file):
        '''
        reads data from file and saves into local variables.
        :param file: the input net cdf file
        '''
        rootgrp = Dataset(file, "r", format="NETCDF4")
        self.time = rootgrp.variables['time']
        self.value = rootgrp.variables['value']
        # find all value attributes
        valueAttributes = rootgrp.variables['value'].ncattrs()
        self.scale = np.nan
        self.offset = np.nan
        self.valueUnits = ''
        for attr in valueAttributes:
            if attr.lower() == 'scale':
                self.scale = float(getattr(rootgrp.variables['value'],attr))
            elif attr.lower() == 'offset':
                self.offset = float(getattr(rootgrp.variables['value'],attr))
            elif  attr.lower() == 'units':
                self.valueUnits = str(getattr(rootgrp.variables['value'],attr))
            elif attr.lower() == 'unit':
                self.valueUnits = str(getattr(rootgrp.variables['value'], attr))
        # find time units
        timeAttributes = rootgrp.variables['time'].ncattrs()
        self.timeUnits = ''
        for attr in timeAttributes:
            if attr.lower() == 'units':
                self.timeUnits = str(getattr(rootgrp.variables['time'], attr))
            elif attr.lower() == 'unit':
                self.timeUnits = str(getattr(rootgrp.variables['time'], attr))
        # check to make sure scale, offset and units were found
        if self.scale == np.nan:
            raise ValueError('There is no scale attribute for the value variable. ')
        elif self.timeUnits == '':
            raise ValueError('There is no units attribute for the time variable. ')
        elif self.valueUnits == '':
            raise ValueError('There is no units attribute for the value variable. ')
        elif self.offset == np.nan:
            raise ValueError('There is no offset attribute for the value variable. ')