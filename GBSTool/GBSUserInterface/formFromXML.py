#creates a dynamic form based on the information in xml files
from PyQt5 import QtWidgets, QtCore, QtGui

class formFromXML(QtWidgets.QDialog):
    def __init__(self, component, componentSoup, write=True):
        super().__init__()
        self.componentType = component.type
        self.componentName = component.component_name
        self.soup = componentSoup
        self.fileDir = component.component_directory
        self.write = write
        self.changes={}
        self.initUI()

    # initialize and display the form
    def initUI(self):
        #container widget
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


    #create a layout from the xml that was turned into soup
    #BeautifulSoup QVBoxLayout -> QVBoxLayout
    def displayXML(self, soup, vlayout):
        from bs4 import Comment
        from ProjectSQLiteHandler import ProjectSQLiteHandler
        from gridLayoutSetup import setupGrid
        g1 = {'headers': [1,2,3,4,5],
              'rowNames': [],
              'columnWidths': [2, 1, 1, 1, 1]}

        #this uses a generic units table
        dbHandler = ProjectSQLiteHandler('project_manager')
        units = dbHandler.cursor.execute("select code from ref_units").fetchall()
        dbHandler.closeDatabase()

        units = [u[0] for u in units]


        for tag in soup.find_all():
            if tag.name not in ['component','childOf','type']:
                row = 0
                hint = "".join(tag.findAll(text=True))

                #the tag name is the main label
                if tag.parent.name not in ['component', 'childOf', 'type']:
                    parent = tag.parent.name
                    pt = '.'.join([parent, tag.name])
                else:
                    pt = tag.name
                g1['rowNames'].append(pt)
                g1['rowNames'].append(pt + 'input' + str(row))
                #every tag gets a grid for data input
                #there are 4 columns - 2 for labels, 2 for values
                #the default is 2 rows - 1 for tag name, 1 for data input
                #more rows are added if more than 2 input attributes exist

                #create the overall label
                g1[pt] = {1:{'widget':'lbl','name':tag.name}}
                column = 1
                g1[pt + 'input' + str(row)] ={}
                for a in tag.attrs:
                    name = '.'.join([pt,str(a)])
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
                        items = units
                    #if the value is set to true false use a checkbox
                    if inputValue in ['TRUE','FALSE']:
                        widget = 'chk'

                #first column is the label
                    g1[pt + 'input' + str(row)][column] = {'widget':'lbl','name':'lbl' + a, 'default':a, 'hint':hint}
                    column+=1

                    if items is None:
                        g1[pt + 'input' + str(row)][column] = {'widget': widget, 'name':name, 'default':inputValue, 'hint':hint}
                    else:
                        g1[pt + 'input' + str(row)][column] = {'widget': widget, 'name':name, 'default': inputValue, 'items':items, 'hint':hint}
        print(g1)
        #make the grid layout from the dictionary
        grid = setupGrid(g1)
        #add the grid to the parent layout
        vlayout.addLayout(grid)

        return vlayout

    #updates the soup to reflect changes in the form
    #None->None
    def update(self):

        #for every tag in the soup fillSetInfo its value from the form
        for tag in self.soup.find_all():
            if tag.parent.name not in ['component', 'childOf', 'type']:
                parent = tag.parent.name
                pt = '.'.join([parent,tag.name])
            else:
                pt = tag.name
            for a in tag.attrs:
                widget = self.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox,QtWidgets.QCheckBox), '.'.join([pt,str(a)]))

                if type(widget) == QtWidgets.QLineEdit:
                    if tag.attrs[a] != widget.text():
                        self.changes['.'.join([pt, str(a)])]=widget.text()
                        tag.attrs[a] = widget.text()

                elif type(widget) == QtWidgets.QComboBox:
                    if tag.attrs[a] != widget.currentText():
                        self.changes['.'.join([pt, str(a)])]=widget.currentText()
                        tag.attrs[a]= widget.currentText()

                elif type(widget) == QtWidgets.QCheckBox:


                    if (widget.isChecked()) & (tag.attrs[a] != 'TRUE'):
                        self.changes['.'.join([pt, str(a)])]= 'TRUE'
                        tag.attrs[a] = 'TRUE'
                    elif (not widget.isChecked()) & (tag.attrs[a] != 'FALSE'):
                        self.changes['.'.join([pt, str(a)])]= 'TRUE'
                        tag.attrs[a]= 'FALSE'

    #when the form is closed the soup gets updated and writtent to an xml file
    #Event -> None
    def closeEvent(self,evnt):
        from GBSController.UIToHandler import UIToHandler

        print('closing descriptor file')
        #fillSetInfo soup
        self.update()
        #Tell the controller to tell the InputHandler to write the xml
        if self.write:
            handler = UIToHandler()
            handler.writeComponentSoup(self.componentName, self.fileDir, self.soup)
        else:
            #return a list of changes
            print(self.changes)