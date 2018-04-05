
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from UISetupForm import SetupForm

from WizardTree import WizardTree
import unittest


dlist = [
            [{'title': 'Output Unit', 'prompt': 'Select the units for the output time interval',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_time_units', 'name': 'outputTimeStepunit', 'folder': False},
             'Output Timestep'],

            [{'title': 'Output Timestep', 'prompt': 'Enter the output timestep',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'outputTimeStepvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Input Unit', 'prompt': 'Select the units for the input time interval',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_time_units', 'name': 'inputimeStepunit', 'folder': False},
             'Input Timestep'],

            [{'title': 'Input Timestep', 'prompt': 'Enter the input timestep',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'inputTimeStepvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Load Profile Units', 'prompt': 'Select the units for the load profile values.',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_load_units', 'name': 'realLoadChannelunit', 'folder': False},
             'Load Profile'],
            [{'title': 'Load Profile', 'prompt': 'Enter the name of the field load Profile values.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'realLoadChannelvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Time Series Date Format', 'prompt': 'Select the date format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_datetime_format', 'name':'dateChannelformat','folder':False}, 'Time Series Date Column'],

            [{'title': 'Time Series Date Column', 'prompt': 'Enter the name of the field containing date data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'dateChannelvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Time Series Time Format', 'prompt': 'Select the date format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_datetime_format', 'name': 'timeChannelformat', 'folder': False},
             'Time Series Time Column'],

            [{'title': 'Time Series Time Column', 'prompt': 'Enter the name of the field containing date data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'timeChannelvalue', 'folder': False},
             'Raw Time Series'],

            [{'title': 'Raw Time Series', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name':'inputFileDir','folder':True}, 'Data Input Format'],

            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name':'hydroFileDir','folder':True}, 'Data Input Format'],

            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name':'windFileDir','folder':True}, 'Data Input Format'],

            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': 'ref_data_format','name':'inputFileFormat', 'folder':False}, 'Project Name'],

            [{'title': 'Project Name', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name':'project', 'folder':False}, None, ]

        ]


def buildWizardTree(dlist):
    w1 = WizardTree(dlist[0][0], dlist[0][1], 0, [])  # output timestep unit
    w2 = WizardTree(dlist[1][0], dlist[1][1], 4, [w1])  # output timestep value

    w3 = WizardTree(dlist[2][0], dlist[2][1], 0, [])  # input units
    w4 = WizardTree(dlist[3][0], dlist[3][1], 3, [w3])  # input value

    w5 = WizardTree(dlist[4][0], dlist[4][1], 0, [])  # load units
    w6 = WizardTree(dlist[5][0], dlist[5][1], 2, [w5])  # load column

    w7 = WizardTree(dlist[6][0], dlist[6][1], 0, [])  # Date Format
    w8 = WizardTree(dlist[7][0], dlist[7][1], 1, [w7])  # Date Column

    w9 = WizardTree(dlist[8][0], dlist[8][1], 0, [])  # Time Format
    w10 = WizardTree(dlist[9][0], dlist[9][1], 0, [w9])  # Time Column

    w11 = WizardTree(dlist[10][0], dlist[10][1], 2, [w10, w8, w6, w4, w2])  # Time Series
    w12 = WizardTree(dlist[11][0], dlist[11][1], 1, [])  # hydro
    w13 = WizardTree(dlist[12][0], dlist[12][1], 0, [])  # wind

    w14 = WizardTree(dlist[13][0], dlist[13][1], 0, [w12, w11, w13])  # inputFileFormat
    w15 = WizardTree(dlist[14][0], dlist[14][1], 0, [w14])
    return w15


W = buildWizardTree(dlist)

print(W.getDialog('Output Unit')[0].key)
print(W.getNext('Output Unit').key)
print((W.getDialog('Time Series Time Format')[0].isLast()))

