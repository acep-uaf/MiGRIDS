
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
#from UISetupForm import SetupForm
from WizardTree import WizardTree
import unittest


def buildWizardTree(wt, dlist, i):
    if i >= len(dlist):
        return wt
    else:
        if dlist[i][3] is not None:
            childlist = []
            for c in dlist[i][3]:
                childlist.append(dlist[c])
        else:
            childlist = []

        if wt is None:

            return WizardTree(dlist[i][0], dlist[i][1], dlist[i][2], buildWizardTree(wt, childlist, i))
        else:

            return wt.insertDialog(
                WizardTree(dlist[i][0], dlist[i][1], dlist[i][2], buildWizardTree(wt, childlist, i)))


dlist = [
            [{'title': 'Time Series Date Format', 'prompt': 'Select the date format for the time series.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Raw Time Series', 0, None],
            [{'title': 'Raw Time Series', 'prompt': 'Select the folder that contains time series data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 2, [0]],
            [{'title': 'Load Hydro Data', 'prompt': 'Select the folder that contains hydro speed data.',
              'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 1, None],
            [{'title': 'Load Wind Data', 'prompt': 'Select the folder that contains wind speed data.', 'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Data Input Format', 0, None],
            [{'title': 'Data Input Format', 'prompt': 'Select the format your data is in.', 'sqltable': None,
              'sqlfield': None, 'reftable': None}, 'Project Name', 0, [1, 2, 3]],
            [{'title': 'Project Name', 'prompt': 'Enter the name of your project'}, None, 0, [4]]

        ]
wt = buildWizardTree(None,dlist,0)
print(wt.children)