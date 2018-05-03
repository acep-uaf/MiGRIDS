#MainForm is the parent for for all sections of the User Interface
#it consists of a navigation tree and pages
from PyQt5 import QtWidgets, QtCore, QtGui
from ConsoleDisplay import ConsoleDisplay
from FormSetup import FormSetup

class MainForm(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setObjectName("mainForm")
        self.layoutWidget = QtWidgets.QWidget(self)
        windowLayout = QtWidgets.QHBoxLayout()
        docker = QtWidgets.QDockWidget()

        self.treeBlock = self.createNavTree()
        docker.setWidget(self.treeBlock)
        self.pageBlock = self.createPageBlock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1),docker,QtCore.Qt.Vertical)


        # add a console window
        self.addConsole()
        docker2 = QtWidgets.QDockWidget()
        docker2.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(8),docker2,QtCore.Qt.Horizontal)
        self.console.showMessage("This is where messages will appear")

        self.setCentralWidget(self.pageBlock)
        # Main title
        self.setWindowTitle('GBS')

        # show the form
        self.showMaximized()

    # add a console block to display messages
    def addConsole(self):
        c = ConsoleDisplay()
        self.console = c

    #NavTree is a navigation tree for switching between pages or sections within pages
    #-> QTreeView
    def createNavTree(self):

        self.data = [
            ('Setup', [
                ('Input Files',[]),
                ('Format',[]),
                ('Environment',[]),
                ('Components',[])
            ]),
            ('Model Runs', [
                ('Sets',[]),
                ('Runs',[]),
                ('Results',[])

            ]),
            ('Optimize',[

            ])
        ]
        self.focusObjects = {'Input Files':FormSetup.functionForCreateButton,
                             'Format':'format',
                             'Environemnt':'environment',
                             'Components':'components',

                             'Sets':'modelSets',
                             'Runs':'runResults',
                             'Results':'modelResults'

        }

        tree = QtWidgets.QTreeView()
        tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tree.clicked.connect(self.switchFocus)
        model = QtGui.QStandardItemModel()
        self.addItems(model,self.data)
        tree.setModel(model)
        model.setHorizontalHeaderLabels([self.tr("Navigation")])

        return tree
    #add navigation items to the navigation tree
    def addItems(self, parent, elements):
        for text, children in elements:
            item = QtGui.QStandardItem(text)
            item.setEditable(False)
            parent.appendRow(item)

            if children:
                self.addItems(item,children)
        return

    def switchFocus(self, position):
        #what item is selected
        indexes = self.treeBlock.selectedIndexes()
        level = 0
        #if a sub-tree branch was selected
        if len(indexes) > 0:
            #this is the leaf
            index = indexes[0]
            #index becomes the root node, level is the steps removed
            while index.parent().isValid():
                index = index.parent()
                level +=1
        #change the active tab depending on the selection
        self.pageBlock.setCurrentIndex(index.row())
        # change the focus depending on the selection
        if level == 1:
           name = list(self.treeBlock.model().itemData(position).values())[0]
           print(name)

           focusObject = self.focusObjects[name]

           if type(focusObject) is str:

               focusWidget = self.pageBlock.currentWidget().findChild(QtWidgets.QWidget,focusObject)
               focusWidget.setFocus(True)
           else:

               #launch the method
               subforms = self.pageBlock.currentWidget().children()
               for s in subforms:

                   if focusObject.__name__ in dir(s):
                       focusObject(s)

        return

    def closeEvent(self,event):
        p = self.findChild(QtWidgets.QWidget,'setupDialog')
        p.close()

    #page block contains all the forms
    def createPageBlock(self):

        pageBlock = PageBlock()

        return pageBlock

class PageBlock(QtWidgets.QTabWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        from FormSetup import FormSetup
        from FormModelRuns import FormModelRun
        from FormContainer import FormContainer
        from ResultsSetup import ResultsSetup
        from FormOptimize import FormOptimize
        from ResultsModel import ResultsModel
        from ResultsOptimize import ResultsOptimize

        #here is where we initilize this subclass

        self.addTab(FormContainer(self,[FormSetup(self), ResultsSetup(self)]), 'Setup')

        self.addTab(FormContainer(self,[FormModelRun(self), ResultsModel(self)]),'Model')
        self.addTab(FormContainer(self, [FormOptimize(self), ResultsOptimize(self)]),'Optimize')

        return

    def closeEvent(self):
        import os
        import shutil
        setupForm = self.findChild(QtWidgets.QWidget,'setupDialog')
        # move the default database to the project folder and save xmls
        if 'projectFolder' in setupForm.model.__dict__.keys():
            path = os.path.dirname(__file__)
            print('Database was saved to %s' % self.model.projectFolder)
        #TODO uncomment once testing complete
            #shutil.move(os.path.join(path, 'project_manager'),
            #            os.path.join(self.model.projectFolder, 'project_manager'))
        #else:
            # if a project was never set then just close and remove the default database
            #os.remove('project_manager')