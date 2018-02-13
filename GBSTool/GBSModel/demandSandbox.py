# create instance
import os
import numpy as np
from Demand import Demand

timeStep = 1
loadRealFiles = [
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\gen1P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\gen2P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\gen3P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg1P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg2P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg3P.nc',
    'C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools\GBSProjects\Chevak\InputData\TimeSeriesData\ProcessedData\wtg4P.nc']


D1 = Demand(timeStep, loadRealFiles)

print('done')