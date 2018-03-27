
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
#from UISetupForm import SetupForm
from WizardTree import WizardTree
import unittest





dlist = [
            [{'title': 'Time Series Date Format', 'prompt': 'Select the date format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Raw Time Series', 0, []],
            [{'title': 'Raw Time Series', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 2, [0]],
            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 1, []],
            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 0, []],
            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Project Name', 0, [1, 2, 3]],
            [{'title': 'Project Name', 'prompt': 'Enter the name of your project'}, None, 0, [4]]

        ]
w1 = WizardTree(dlist[0][0], dlist[0][1], dlist[0][2], [])
w2 = WizardTree(dlist[1][0], dlist[1][1], dlist[1][2], [w1])
w3 = WizardTree(dlist[2][0], dlist[2][1], dlist[2][2], [])
w4 = WizardTree(dlist[3][0], dlist[3][1], dlist[3][2], [])
w5 = WizardTree(dlist[4][0], dlist[4][1], dlist[4][2], [w2, w3, w4])
w6 = WizardTree(dlist[5][0], dlist[5][1], dlist[5][2], [w5])

print(w6.getDialog('Load Hydro Data')[0].key)