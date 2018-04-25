#MainForm is the parent for for all sections of the User Interface
#it consists of a navigation tree and pages
from PyQt5 import QtWidgets, QtCore, QtGui
from ConsoleDisplay import ConsoleDisplay

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

        data = [
            ('Setup', [
                ('Input Files',[]),
                ('Format',[]),
                ('Environment',[]),
                ('Components',[]),
                ('Load Data',[])
            ]),
            ('Data Input', [

            ]),
            ('Model Runs', [
                ('Sets',[]),
                ('Runs',[]),
                ('Results',[])

            ]),
            ('Optimize',[

            ])
        ]
        tree = QtWidgets.QTreeView()
        tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.openMenu)
        model = QtGui.QStandardItemModel()
        self.addItems(model,data)
        tree.setModel(model)
        model.setHorizontalHeaderLabels([self.tr("Navigation")])

        return tree
    def addItems(self, parent, elements):
        for text, children in elements:
            item = QtGui.QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.addItems(item,children)
        return

    def openMenu(self, position):
        indexes = self.treeBlock.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            #this gets the top level of the selected item
            while index.parent().isValid():
                index = index.parent()
                level +=1

                menu = QtWidgets.QMenu()
                menu.addAction(self.tr("edit"))
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Level",
                                                "You are on level %s" %level)
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()
                model = self.treeBlock.model()
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Index Object",
                                            "You are going to %s" % model.data(index))
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()
                menu.exec_(self.treeBlock.viewport().mapToGlobal(position))

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
        #here is where we initilize this subclass

        self.addTab(FormContainer(self,[FormSetup(self), ResultsSetup(self)]), 'Setup')
        self.addTab(FormSetup(self), 'Input Data')
        self.addTab(FormModelRun(self), 'Model')
        self.addTab(FormSetup(self), 'Optimize')

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