# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu, Alaska Center for Energy and Power
# Date: October 3, 2018
# License: MIT License (see LICENSE file of this package for more information)

# imports
import importlib.util
import os
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as Soup
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../Controls'))

def loadControlModule(controlFile,controlInputsFile,controlClass):
    # import control class
    modPath, modFile = os.path.split(controlFile)
    # if located in a different directory, add to sys path
    if len(modPath) != 0:
        sys.path.append(modPath)
    # split extension off of file
    modFileName, modFileExt = os.path.splitext(modFile)
    # import module
    A = importlib.import_module(modFileName)
    # get the inputs
    rdi = open(controlInputsFile, "r")
    controlInputsXml = rdi.read()
    rdi.close()
    controlInputsSoup = Soup(controlInputsXml, "xml")

    # get all tags
    elemList = []
    xmlTree = ET.parse(controlInputsFile)
    for elem in xmlTree.iter():
        elemList.append(elem.tag)

    # create Dict of tag names and values (not including root)
    controlInputs = {}
    for elem in elemList[1:]:
        controlInputs[elem] = returnObjectValue(controlInputsSoup.find(elem).get('value'))

    # check if inputs for initializing controller
    if len(controlInputs) == 0:
        return getattr(A,controlClass)()
    else:
        return getattr(A,controlClass)(controlInputs)

# return int, float, bool or string depending on what it can be converted into.
def returnObjectValue(obj):
    if isint(obj):
        return int(obj)
    elif isfloat(obj):
        return float(obj)
    elif isbool(obj):
        if obj.lower == 'true':
            return True
        else:
            return False
    else:
        return str(obj)

# test if an object is a float
def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

# test if an object is an interger
def isint(x):
    try:
        a = int(x)
    except ValueError:
        return False
    else:
        return True

# test if an object is a bool
def isbool(x):
    if x.lower() in ['false', 'true']:
        return True
    else:
        return False