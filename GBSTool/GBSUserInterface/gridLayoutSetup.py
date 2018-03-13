# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 08:58:02 2018

@author: tcmorgan2
"""

from PyQt5 import QtCore, QtGui, QtWidgets 

def setupGrid(inputDictionary):
      def getColumn(objectName, row, c, gridLayout):
       o =gridLayout.itemAtPosition(0,c)
       if c > gridLayout.columnCount():
           return False
       if o is not None:
           o = o.widget()
           n = o.objectName()
           if n == objectName:
               return c
       return getColumn(objectName,row,c+1,gridLayout)
   
      def getWidget(stringType):
           choices={'combo':QtWidgets.QComboBox(),'txt':QtWidgets.QLineEdit()}
           result = choices.get(stringType,QtWidgets.QTextEdit())
           return result     
      font = QtGui.QFont()
      font.setPointSize(26)
             #grid block layout
      grid = QtWidgets.QGridLayout()
      grid.setContentsMargins(0, 0, 0, 0)
      grid.setObjectName("grdSetup")
            
      headers = inputDictionary['headers']
            
      for i in range(len(headers)):
         grid.lbl = QtWidgets.QLabel()        
         grid.lbl.setFont(font)
         grid.lbl.setObjectName('lbl' + headers[i])
         grid.addWidget(grid.lbl, 0, i, 1, 1)
         grid.lbl.setText(headers[i])
         rowNames = inputDictionary['rowNames']
            
      for i in range(len(rowNames)):
          grid.lbl = QtWidgets.QLabel()        
          grid.lbl.setFont(font)
          grid.lbl.setObjectName('lbl' + rowNames[i])
          grid.addWidget(grid.lbl, i+1, 0, 1, 1)
          grid.lbl.setText(rowNames[i])  
                
                #get the row of widgets
          r = inputDictionary[rowNames[i]]
                #there will be a value for every column except the first one
          for h in headers[1:]:
              grid.wid=getWidget(r[h]['widget'])
              grid.wid.setFont(font)
              grid.wid.setObjectName('inp'.join(r).join(h))
              grid.addWidget(grid.wid,i+1,getColumn('lbl' + h,i,1,grid),1,1)
              if 'items' in r[h].keys():
                  for item in r[h]['items']:
                      grid.wid.addItem(item)
                                   

      return grid