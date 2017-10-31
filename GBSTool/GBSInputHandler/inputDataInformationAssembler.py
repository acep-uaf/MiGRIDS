# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 30, 2017
# License: MIT License (see LICENSE file of this package for more information

# General Imports
import numpy as np
import pandas as pd


'''
The inputDataInformation class holds the information gathered from the inputDataInformationInterface.xml 
file. 
INPUTS: 
    

OUTPUTS:
    
'''
class inputDataInformation:

    # ------Variable definitions-------
    # ******Input variables************
    # project name
    projectName = []
    # directory of input files
    inputFileDir = ''
    #
    inputFileType = ''
    #
    inputFileFormat = ''
    #
    componentChannels = pd.DataFrame(data={'headerName':(),'componentName':(),'componentAttribute':()})
    componentChannels
    # ******Internal variables*********










