#creates a dynamic form based on the information in xml files
from PyQt5 import QtWidgets

class formFromXML(QtWidgets.QDialog):
    def __init__(self, componentType):
        super().__init__()
        self.componentType = componentType
        self.initUI()
#initialize and display the form
    def initUI(self):
        self.setObjectName("Component Dialog")
        windowLayout = QtWidgets.QVBoxLayout()

        self.soup = self.readXML(self.componentType)

        self.layout = self.displayXML(self.soup, windowLayout)
        self.setLayout(self.layout)
        self.showMaximized()
        self.exec()

#read in the xml files that the form will be based on
    #String -> BeautifulSoup
    def readXML(self, componentType):
        from bs4 import BeautifulSoup
        import os
        #xml templates are in the model/resources/descriptor folder
        here = os.path.dirname(os.path.realpath(__file__))
        componentPath = os.path.join(here, '../GBSModel/Resources/Components')
        # get list of component prefixes that correspond to componentDescriptors

        # read the xml file
        os.chdir(componentPath)
        fileName = os.path.join(componentPath,componentType + 'Descriptor.xml')  # get filename
        infile_child = open(fileName, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
        parent = soup.childOf.string  # find the anme of parent. if 'self', no parent file

        while parent != 'self':  # continue to iterate if there are parents
            fileName = parent + '.xml'
            infile_child = open(fileName, "r")
            contents_child = infile_child.read()
            infile_child.close()
            soup2 = BeautifulSoup(contents_child, 'xml')
            # find parent. if 'self' then no parent
            parent = soup2.childOf.string

            for child in soup2.component.findChildren():  # for each tag under component
                # check to see if this is already a tag. If it is, it is a more specific implementation, so don't add
                # from parent file
                if soup.component.find(child.name) is None:
                    soup.component.append(child)

        return soup
    #create a layout from the xml
    #BeautifulSoup -> QGroupBox
    def displayXML(self, soup, vlayout):
        from gridLayoutSetup import setupGrid
        g1 = {'headers': [1,2,3,4,5],
              'rowNames': [],
              'columnWidths': [2, 1, 1, 1, 1]}
        print(g1)
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
                print(g1)
                #create the overall label
                g1[tag.name] = {1:{'widget':'txt','name':tag.name}}
                column = 1
                g1[tag.name + 'input' + str(row)] ={}
                for a in tag.attrs:
                    inputValue = tag[a]
                    #columns aways starts populating at 2

                    if column <=4:
                       column+=1
                       print(column)
                    else:
                       column = 2
                       row+=1


                    # if a = 'unit':
                    #     #generate combo box
                    #

                    # if inputValue in ['TRUE','FALSE']:
                    #     #generate a combo box and populate with true/False
                #first column is the label
                    g1[tag.name + 'input' + str(row)][column] = {'widget':'lbl','name':a}
                    column+=1
                    print(column)
                    g1[tag.name + 'input' + str(row)][column] = {'widget': 'txt', a:inputValue}
        g1 = {'headers': [1, 2, 3, 4, 5],
         'rowNames': ['powerCurveDataPoints', 'powerCurveDataPointsinput0', 'ws', 'wsinput0', 'pPu', 'pPuinput0'],
         'columnWidths': [2, 1, 1, 1, 1],
         'powerCurveDataPoints': {1: {'widget': 'txt', 'name': 'powerCurveDataPoints'}},
         'powerCurveDataPointsinput0': {}, 'ws': {1: {'widget': 'txt', 'name': 'ws'}},
         'wsinput0': {2: {'widget': 'lbl', 'name': 'lblvalue'}, 3: {'widget': 'txt', 'name': 'value', 'default':'0 0'},
                      4: {'widget': 'lbl', 'name': 'lblunit'}, 5: {'widget': 'txt', 'name':'unit','default': 'm/s'}},
         'pPu': {1: {'widget': 'txt', 'name': 'pPu'}},
         'pPuinput0': {2: {'widget': 'lbl', 'name': 'value'}, 3: {'widget': 'txt', 'name': 'value', 'default': '1'},
                       4: {'widget': 'lbl', 'name': 'unit'}, 5: {'widget': 'txt', 'name':'unit', 'default': 'pu'}},
         }
        #TODO remove test
        #g1['rowNames'] = g1['rowNames'][0:10]
        grid = setupGrid(g1)
        vlayout.addLayout(grid)

        return vlayout

    def createLayout(self):
        #add xml input layout
        #add nav buttons
        return