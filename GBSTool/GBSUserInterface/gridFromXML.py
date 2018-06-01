#creates a dynamic form based on the information in xml files
from PyQt5 import QtWidgets, QtCore, QtGui

class gridFromXML(QtWidgets.QHBoxLayout):
    def __init__(self, componentSoup, fields = [],write=True):
        super().__init__()
        self.fields = fields

        self.soup = componentSoup

        self.write = write
        self.changes={}
        gb = self.displayXML(self.soup, QtWidgets.QVBoxLayout())
        self.addLayout(gb)


    #create a layout from the xml that was turned into soup
    #BeautifulSoup QVBoxLayout -> QVBoxLayout
    def displayXML(self, soup, vlayout):
        from bs4 import Comment
        from GBSUserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
        from GBSUserInterface.gridLayoutSetup import setupGrid
        g1 = {'headers': [1,2,3,4,5],
              'rowNames': [],
              'columnWidths': [2, 1, 1, 1, 1]}

        #this uses a generic units table

        for tag in soup.find_all():
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
                print(a)
                name = '.'.join([pt,str(a)])


                inputValue = tag[a]
                #columns aways starts populating at 2
                if a != 'choices':

                    if column <=4:
                       column+=1
                    else:
                       column = 2
                       row+=1

                    widget = 'txt'
                    items = None
                    #if setting units attribute use a combo box
                    if 'choices' in tag.attrs:
                        widget = 'combo'
                        items = tag['choices'].split(' ')

                    #if the value is set to true false use a checkbox
                    if a == 'active':
                        widget = 'chk'
                    if a == 'mode':
                        widget = 'txt'
                        items = None
                #first column is the label
                    g1[pt + 'input' + str(row)][column] = {'widget':'lbl','name':'lbl' + a, 'default':a, 'hint':hint}
                    print(g1)
                    column+=1

                    if items is None:
                        g1[pt + 'input' + str(row)][column] = {'widget': widget, 'name':name, 'default':inputValue, 'hint':hint}
                    else:
                        g1[pt + 'input' + str(row)][column] = {'widget': widget, 'name':name, 'default': inputValue, 'items':items, 'hint':hint}

        #make the grid layout from the dictionary
        grid = setupGrid(g1)
        #add the grid to the parent layout
        vlayout.addLayout(grid)

        return vlayout

    #updates the soup to reflect changes in the form
    #None->None
    def update(self):

        #for all the  children on the form update their values in the project database
        return
