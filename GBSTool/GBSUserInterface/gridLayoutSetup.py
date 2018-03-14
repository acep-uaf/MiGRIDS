# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 08:58:02 2018

@author: tcmorgan2
"""

from PyQt5 import QtCore, QtGui, QtWidgets


def setupGrid(inputDictionary):
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

    def getWidget(stringType):
        # TODO add multiline to choices
        choices = {'combo': QtWidgets.QComboBox(), 'txt': QtWidgets.QLineEdit(),
                   'btn': QtWidgets.QPushButton(), 'chk': QtWidgets.QCheckBox(), 'lbl': QtWidgets.QLabel()}
        result = choices.get(stringType, QtWidgets.QTextEdit())
        return result

    font = QtGui.QFont()
    font.setPointSize(26)
    # grid block layout
    grid = QtWidgets.QGridLayout()
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setObjectName("grdSetup")

    headers = inputDictionary['headers']

    def getPosition(i, widthList):
        x = sum(widthList[:i]) + 1

        return x

    for i in range(len(headers)):
        # the x position is the sum of previous widths
        xpos = getPosition(i, inputDictionary['columnWidths'])
        grid.lbl = QtWidgets.QLabel()
        grid.lbl.setFont(font)

        grid.lbl.setObjectName('lbl' + str(headers[i]))
        grid.lbl.setProperty('wscale', inputDictionary['columnWidths'][i])
        grid.lbl.setProperty('xpos', xpos)
        grid.addWidget(grid.lbl, 0, xpos, 1, inputDictionary['columnWidths'][i])
        if type(headers[i]) == str:
            grid.lbl.setText(headers[i])
    rowNames = inputDictionary['rowNames']
    print(rowNames)
    # TODO combo boxes need padding

    for i in range(len(rowNames)):
        print(rowNames[i])
        print(i)
        grid.lbl = QtWidgets.QLabel()
        grid.lbl.setFont(font)
        grid.lbl.setObjectName('lbl' + str(rowNames[i]))
        grid.addWidget(grid.lbl, i + 1, 0, 1, 1)
        if type(rowNames[i]) == str:
            grid.lbl.setText(rowNames[i])

        # get the row of widgets
        r = inputDictionary[rowNames[i]]
        # fill in row values
        for h in headers[1:]:
            # identify what kind of widget it is
            grid.wid = getWidget(r[h]['widget'])

            # find the column width from the column label width

            w = getColumn('lbl' + str(h), 0, 0, grid)
            pscale = w.property('wscale')
            xpos = w.property('xpos')

            # if there is an icon set it
            if 'icon' in r[h].keys():
                grid.wid.setIcon(grid.wid.style().standardIcon(getattr(QtWidgets.QStyle, r[h]['icon'])))
            grid.wid.setFont(font)
            grid.wid.setObjectName('inp'.join(str(r)).join(str(h)))

            grid.addWidget(grid.wid, i + 1, xpos, 1, pscale)

            if 'items' in r[h].keys():
                for item in r[h]['items']:
                    grid.wid.addItem(item)

    return grid
