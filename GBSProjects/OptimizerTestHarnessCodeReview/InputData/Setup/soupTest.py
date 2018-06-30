#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 10:49:52 2018

@author: marcmueller-stoffels
"""
from bs4 import BeautifulSoup 

# open file and read into soup
infile_child = open('../../OutputData/Set0/Setup/Igiugig0Set2Setup.xml', "r")  # open
contents_child = infile_child.read()
infile_child.close()
soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

