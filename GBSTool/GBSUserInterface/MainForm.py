#MainForm is the parent for for all sections of the User Interface
#it consists of a navigation tree and pages
from PyQt5 import QtWidgets, QtCore, QtGui

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

        #windowLayout.addWidget(self.treeBlock)
        self.setCentralWidget(self.pageBlock)
        #windowLayout.addWidget(self.pageBlock)
        #self.layoutWidget.setLayout(windowLayout)
        # Main title
        self.setWindowTitle('GBS')

        # show the form
        self.showMaximized()


    #NavTree is a navigation tree for switching between pages or sections within pages
    #-> QTreeView
    def createNavTree(self):

        data = [
            ('Setup', [
                ('Format',[]),
                ('Environment',[]),
                ('Components',[]),
                ('Load Data',[])
            ]),
            ('Data Input', [

            ]),
            ('Model Runs', [
                ('Base Case',[]),
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



    #page block contains all the forms
    def createPageBlock(self):

        pageBlock = PageBlock()

        return pageBlock

class PageBlock(QtWidgets.QTabWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        from UISetupForm import SetupForm
        #here is where we initilize this subclass
        self.addTab(SetupForm(),'Setup')
        self.addTab(SetupForm(),'Input Data')
        self.addTab(SetupForm(), 'Model')
        self.addTab(SetupForm(), 'Optimize')

        return