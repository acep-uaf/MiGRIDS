#form for selecting what components to use in a model set
from PyQt5 import QtWidgets, QtCore, QtGui
class ComponentSetListForm(QtWidgets.QDialog):
    #initialize with a list of component names and list of boolean values for whether or not to include
    def __init__(self,components,checked):
        super().__init__()
        self.components = components
        self.checked = checked
        self.init()
        self.setWindowTitle('Select components to include')

    def init(self):
        layout = QtWidgets.QVBoxLayout()
        #make the list widget
        self.listBlock = self.makeListWidget()
        layout.addWidget(self.listBlock)
        self.setLayout(layout)
        self.show()
        self.exec()
        return

    def makeListWidget(self):
       view = QtWidgets.QListWidget()

       for i in range(len(self.components)):
           view.addItem(self.components[i])

       for i in range(view.count()):
           item = view.item(i)
           item.setFlags(QtCore.Qt.ItemIsUserCheckable)
           item.setCheckState(self.checked[i])

       return view
