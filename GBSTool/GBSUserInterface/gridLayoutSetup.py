# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 08:58:02 2018

@author: tcmorgan2
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import re
from GBSUserInterface.Delegates import ClickableLineEdit

#useds locations and values specified in a dictionary to create a grid layout
#dictionary should contain atleast 'headers' and 'rowNames' keys
#headers and rowNames can be numbers in which case they won't be displayed
#Dictionary -> QtGridLayout
def setupGrid(inputDictionary):
    #String, integer, integer, QtGridLayout
    #returns a QtWidget at a specified row, column within a gridlayout
    def getColumn(objectName, row, c, gridLayout):
        o = gridLayout.itemAtPosition(0, c)

        if c > gridLayout.columnCount():
            return False
        if o is not None:
            o = o.widget()
            n = o.objectName()
            if n == objectName:
                return o
        return getColumn(objectName, row, c + 1, gridLayout)

    #String ->QtWidget
    #returns a QtWidget based on a text input
    def getWidget(stringType):
        # TODO add multiline to choices
        choices = {'combo': QtWidgets.QComboBox(), 'txt': QtWidgets.QLineEdit(),
                   'btn': QtWidgets.QPushButton(), 'chk': QtWidgets.QCheckBox(),
                   'lbl': QtWidgets.QLabel(),
                   'lncl':ClickableLineEdit()}
        result = choices.get(stringType, QtWidgets.QTextEdit())
        return result

    font = QtGui.QFont()
    lfont = QtGui.QFont()
    l1font = QtGui.QFont()
    lfont.setBold(True)
    l1font.setBold(True)
    l1font.setPointSize(20)

    # grid block layout
    grid = QtWidgets.QGridLayout()
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setObjectName("inputGrid")

    #list of top row values

    headers = inputDictionary['headers']

    def getPosition(i, widthList):
        x = sum(widthList[:i]) + 1

        return x
    #for all the headers
    for i in range(len(headers)):
        # the x position is the sum of previous widths
        xpos = getPosition(i, inputDictionary['columnWidths'])
        grid.lbl = QtWidgets.QLabel()
        grid.lbl.setFont(lfont)
        #All the headers are label objects with a name beginning with 'lbl'
        grid.lbl.setObjectName('lbl' + str(headers[i]))

        grid.lbl.setProperty('wscale', inputDictionary['columnWidths'][i])
        grid.lbl.setProperty('xpos', xpos)

        grid.addWidget(grid.lbl, 0, xpos, 1, inputDictionary['columnWidths'][i])

        #if the header is a string then add text to the label
        #if its a number don't show the number
        if type(headers[i]) == str:
            grid.lbl.setText(headers[i])
    #A list of row names
    rowNames = inputDictionary['rowNames']

    for i in range(len(rowNames)):
        # for every row name create a label
        grid.lbl = QtWidgets.QLabel()

        grid.lbl.setObjectName('lbl' + str(rowNames[i]))
        grid.addWidget(grid.lbl, i + 1, 1, 1, 1)

        #if the rowname is a string show it otherwise don't

        if type(rowNames[i]) != int:
            if not rowNames[i][len(rowNames[i])-1:].isdigit():
                label = rowNames[i].split('.')[len(rowNames[i].split('.')) - 1]
                #make camelCase space delimited
                label = re.sub("([a-z])([A-Z])","\g<1> \g<2>",label)
                grid.lbl.setText(label)


        # get the row of widgets
        r = inputDictionary[rowNames[i]]
        # if there is no data in the row align right
        if len(r.keys()) <= 1:
            grid.lbl.setAlignment(QtCore.Qt.AlignLeft)
            grid.lbl.setFont(l1font)
        else:
            grid.lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        # fill in row values
        if len(headers) % 2 != 0:
            h_to_fill = headers[1:]
        else:
            h_to_fill = headers
        for h in h_to_fill:

            # identify what kind of widget it is
            if h in r.keys():
                grid.wid = getWidget(r[h]['widget'])

                # find the column width from the column label width
                if type(h) == int:
                    w = getColumn('lbl' + str(h), 0, h, grid)
                else:
                    w = getColumn('lbl' + str(h), 0, headers.index(h), grid)


                pscale = w.property('wscale')
                xpos = w.property('xpos')

                # if there is an icon set it
                if 'icon' in r[h].keys():
                    grid.wid.setIcon(grid.wid.style().standardIcon(getattr(QtWidgets.QStyle, r[h]['icon'])))

                grid.wid.setFont(font)
                #the name matches the name and attribute in the xml file
                grid.wid.setObjectName(r[h]['name'])
                #if it has items they get added
                if 'items' in r[h].keys():
                    for item in r[h]['items']:
                        grid.wid.addItem(item)
                #if there is a hint it gets set
                if 'hint' in r[h].keys():
                    grid.wid.setToolTip(r[h]['hint'])
                    grid.wid.setToolTipDuration(10000)

                if 'default' in r[h].keys():
                    #check what kind of widget it is and set its default value
                    if type(grid.wid) == QtWidgets.QComboBox:

                        #find the position of the defualt value
                        grid.wid.setCurrentIndex(grid.wid.findText(r[h]['default']))

                    elif type(grid.wid) == QtWidgets.QCheckBox:
                        if r[h]['default'] == 'TRUE':
                            grid.wid.setChecked(True)
                    else:
                        grid.wid.setText(r[h]['default'])

                grid.addWidget(grid.wid, i + 1, xpos, 1, pscale)




    return grid
