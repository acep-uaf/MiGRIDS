#creates a dynamic form based on the information in xml files
from PyQt5 import QtWidgets, QtCore, QtGui

class formFromXML(QtWidgets.QDialog):
    def __init__(self, component, componentSoup):
        super().__init__()
        self.componentType = component.type
        self.componentName = component.component_name
        self.soup = componentSoup
        self.fileDir = component.component_directory
        self.initUI()
   #initialize and display the form
    def initUI(self):
        #container
        widget = QtWidgets.QWidget()
        self.setWindowTitle(self.componentName)
        self.setObjectName("Component Dialog")
        #layout of container widget
        windowLayout = QtWidgets.QVBoxLayout()

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        #a grid layout object
        xmlLayout = self.displayXML(self.soup, windowLayout)
        widget.setLayout(xmlLayout)
        scrollArea.setWidget(widget)

        #adding scroll layer
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(scrollArea,6)

        self.setLayout(self.layout)

        self.show()
        self.exec()

#read in the xml files that the form will be based on
    #String -> BeautifulSoup

    #create a layout from the xml
    #BeautifulSoup -> QVBoxLayout
    def displayXML(self, soup, vlayout):
        from gridLayoutSetup import setupGrid
        g1 = {'headers': [1,2,3,4,5],
              'rowNames': [],
              'columnWidths': [2, 1, 1, 1, 1]}

        for tag in soup.find_all():
            if tag.name not in ['component','childOf','type']:
                row = 0
                #the tag name is the main label
                g1['rowNames'].append(tag.name)
                g1['rowNames'].append(tag.name + 'input' + str(row))
                #every tag gets a grid for data input
                #there are 4 columns - 2 for labels, 2 for values
                #the default is 2 rows - 1 for tag name, 1 for data input
                #more rows are added if more than 2 input attributes exist

                #create the overall label
                g1[tag.name] = {1:{'widget':'lbl','name':tag.name}}
                column = 1
                g1[tag.name + 'input' + str(row)] ={}
                for a in tag.attrs:
                    inputValue = tag[a]
                    #columns aways starts populating at 2

                    if column <=4:
                       column+=1

                    else:
                       column = 2
                       row+=1
                    widget = 'txt'
                    items = None
                    #if setting units attribute use a combo box
                    if a =='unit':
                        widget = 'combo'
                        items = 'kW', 'Kvar','m/s'
                    #if the value is set to true false use a checkbox
                    if inputValue in ['TRUE','FALSE']:
                        widget = 'chk'

                #first column is the label
                    g1[tag.name + 'input' + str(row)][column] = {'widget':'lbl','name':'lbl' + a, 'default':a}
                    column+=1

                    if items is None:
                        g1[tag.name + 'input' + str(row)][column] = {'widget': widget, 'name':tag.name + a, 'default':inputValue}
                    else:
                        g1[tag.name + 'input' + str(row)][column] = {'widget': widget, 'name':tag.name + a, 'default': inputValue, 'items':items}

        grid = setupGrid(g1)
        vlayout.addLayout(grid)

        return vlayout

    def update(self):

        #for every tag in the soup update its value from the form
        for tag in self.soup.find_all():
                for a in tag.attrs:
                    widget = self.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox,QtWidgets.QCheckBox), tag.name + str(a))

                    if type(widget) == QtWidgets.QLineEdit:
                        tag.attrs[a] = widget.text()

                    elif type(widget) == QtWidgets.QComboBox:
                        tag.attrs[a]= widget.currentText()

                    elif type(widget) == QtWidgets.QCheckBox:
                        if widget.isChecked():
                             tag.attrs[a] = 'TRUE'
                        else:
                            tag.attrs[a]= 'FALSE'



    def closeEvent(self,evnt):
        from UIToHandler import UIToHandler
        from Component import Component
        print('closing descriptor file')
        #update xml file
        self.update()
        handler = UIToHandler()
        handler.writeSoup(self.componentName,self.fileDir,self.soup)

