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

# change dir to where setup file descriptor is located
import os
here = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(here, '../GBSModel/Resources/Setup')

class inputDataInformation:

    # ------Variable definitions-------
    # ******Input variables************
    # project name
    project.name = []
    # directory of input files
    inputFileDir.value = ''
    #
    inputFileType.value = ''
    #
    inputFileFormat.value = ''
    #
    class componentChannels:
        class headerName:
            value = ()
        class componentName:
            value = ()
    componentChannels.headerName.value = ()
    #
    componentChannels.

    = pd.DataFrame(data={'headerName':(),'componentName':(),'componentAttribute':()})
    componentChannels
    # ******Internal variables*********










