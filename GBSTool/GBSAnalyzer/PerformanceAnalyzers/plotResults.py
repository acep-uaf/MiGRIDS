# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 09:42:42 2018

@author: jbvandermeer
"""

# imports
import sys
import os
import tkinter as tk
from tkinter import filedialog
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../../'))
sys.path.append(here)
from GBSAnalyzer.DataRetrievers.readNCFile import readNCFile
from GBSModel.getSeriesIndecies import getSeriesIndecies
import matplotlib.pyplot as plt
import numpy as np

def plotProjectRun(projectRunDir = '', steps = 'all'):
    
    if projectRunDir == '':
        print('Choose the directory with the output files for the run')
        root = tk.Tk()
        root.withdraw()
        projectRunDir = filedialog.askdirectory()

    # get the run number
    dirName = os.path.basename(projectRunDir)
    try:
        run = int(dirName[3:])
    except ValueError:
        print('The directory name for the simulation run results does not have the correct format. It needs to be \'Runx\' where x is the run number.')


        
        
    # go to project and run directory
    os.chdir(projectRunDir)
    
    # load diesel generator output
    genP = readNCFile('genPRun'+str(run)+'.nc')
    plotIdx = getSeriesIndecies(steps, len(genP))
    # plot generator power
    plt.figure()
    plt.plot(genP.time[plotIdx], np.array(genP.value[plotIdx])*genP.scale + genP.offset)
    plt.savefig('genP')
    plt.show()

    # load wtg import
    wtgImport = readNCFile('wtgPImportRun' + str(run) + '.nc')
    plotIdx = getSeriesIndecies(steps, len(wtgImport))
    # plot wtg import
    plt.figure()
    plt.plot(wtgImport.time[plotIdx], np.array(wtgImport.value[plotIdx]) * wtgImport.scale + wtgImport.offset)
    plt.savefig('wtgImport')
    plt.show()

