# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def getComponentDescriptor(varNames):
    # varNames are the variable names (corresponding to component descriptor file names) to generate a netcdf with

    # temporary fix

    from netCDF4 import Dataset
    ncfile = Dataset('test.nc', 'w', format='NETCDF4')

    import os
    os.chdir('C:\\Users\jbvandermeer\Documents\ACEP\GBS\GBSTools1\InputData\Chevak')
    from bs4 import BeautifulSoup
    infile_child = open("gen1Descriptor.xml", "r")
    contents_child = infile_child.read()
    infile_interface = open('gen1DescriptorInterface.xml','r')
    contents_interface = infile_interface.read()


    soup = BeautifulSoup(contents_child, 'xml')
    titles = soup.find_all('title')
    for title in titles:
    print(title.get_text())

    return ncfile

