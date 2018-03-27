class WizardTree:
    #WizardTree, dictionary, string, integer, ListOfWizardTree -> WizardTree
    def __init__(self, value, parentKey, siblingPosition, lstWizardTree):
        self.key = value['title']
        self.value = value
        self.position = siblingPosition
        self.children = lstWizardTree
        self.parentKey = parentKey
        #adopt the children
        if self.children is not None:
            l = self.children.__iter__()
            self.provideParent(l)
        self.parent = None
        #TODO add findparent
        return

    #if the child parentkey matches the WizardTree's key then that WizardTree becomes its parent.
    def addParent(self,child):
        if child.parentKey == self.key:
            child.parent = self

    #goes through list decendents to add a parent property
    #WizardTree is the parent, loc is list of WizardTree children
    def provideParent(self, loc):

        if loc.__length_hint__() == 0:
            #if loc is empty we don't need to provide any parents
            return None
        else:
            #otherwise the first child gets its parent and the remaining child
            self.addParent(loc.__next__())
            return self.provideParent(loc)



    def getFromList(self, position):
        if self is None:
            return None
        else:
            return self.children[position]

    #returns dialog based on the key
    def getDialog(self, key):
        #if the node provided is the correct one return its value
        if key == self.key:
            return [self] + self.findDialog(self.children.__iter__(),key)

        return self.findDialog(self.children.__iter__(), key)


    def findDialog(self, lod,key):
        #key doesn't exist
        if lod.__length_hint__() ==0:
            return []

        return lod.__next__().getDialog(key) + self.findDialog(lod, key)
    # def getTitle(self):
    #     return self.getTitleList(self.children.__iter__()) + [self.key]
    #
    # def getTitleList(self, lod):
    #     if lod.__length_hint__() ==0:
    #         return []
    #     return lod.__next__().getTitle() + self.getTitleList(lod)

    #self is the parent
    def insertDialog(self, position, node, children):
        self.children.append(WizardTree(node,self.key,position,children))



    #if there are children move through them
    #if there are not any children move up a node and through the rest of those children
        def getNext(self,key):
            #current dialog has children
            if len(self.getDialog(key).children) > 0:
                #go to first child
                return self.getDialog(key).children[0]
            #has no older siblings
            elif self.getDialog(key).position >= len(self.getDialog(key).parent.children):

                return None
            #otherwise get the next oldest sibling
            return self.getDialog(key).parent.children[self.getDialog(key).position +1]
    def getNext(self, key):
        print(self.key)
        print(self.getDialog(key).key)

    #move to previous list item
    #if list is empty move up a node
    def getPrevious(self):
        #up to parent
        try:
            return self.parent.children[self.position -1]
        except IndexError:
            return self.parent

    def getTitle(self):
        return self.getTitleList(self.children.__iter__()) + [self.key]

    def getTitleList(self, lod):
        if lod.__length_hint__() ==0:
            return []
        return lod.__next__().getTitle() + self.getTitleList(lod)

    def getStart(self):
        if self.isStart():
            return self
        return self.parent.getStart()

    def isStart(self):
        if self.parent:
            return False
        return True

    def isLast(self):
        if self.children:
            return False
        if self.parent == None:
            return True
        if self.position == len(self.parent.children):
            return True

        return False
