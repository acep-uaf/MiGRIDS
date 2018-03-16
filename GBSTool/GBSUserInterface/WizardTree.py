class WizardTree:
    #WizardTree, integer, dictionary, WizardTree, WizardTree -> WizardTree
    def __init__(self, key, value, ltree, rtree, parent):
        self.key = key
        self.value = value
        self.ltree = ltree
        self.rtree = rtree
        self.parent = parent
        return

    def getRecord(self, key):
        if self is None:
            return None
        elif self.key == key:
            return self.value
        elif self.key < key:
            return self.getRecord(self.rtree,key)
        else:
            return self.getRecord(self.ltree, key)

    def insert(self, node):
        if self is None:
            return None
        elif self.key == node.key:
            return self
        elif self.key < node.key:
            if self.ltree is None:
                self.ltree = node
                return self
            else:
                return self.insert(self.ltree, node)
        else:
            if self.rtree is None:
                self.rtree = node
                return self
            else:
                return self.insert(self.rtree, node)


