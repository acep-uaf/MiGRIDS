class WizardTree:
    #WizardTree, dictionary, string, integer, ListOfWizardTree -> WizardTree
    def __init__(self, value, parentKey, siblingPosition, lstWizardTree):
        self.key = value['dialog_name']
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

    #returns the value portion of a dialog node
    def getDialog(self, key):
        #if the node provided is the correct one return its value
        if key == self.key:
            return self.value
        #otherwise search for the correct node in the baseTree
        if self.children is not None:
            c = self.children.__iter__()
            return self.findDialog(c,key)
        return None



    def findDialog(self, c, key):

        if self is None:
            #key doesn't exist
            return None
        elif self.parent is not None:
             if self.parent.getDialog(key) == key:
                return self.parent
        return c.__next__().getDialog(key)
#TODO not used
    #self is the parent
    def insertDialog(self, position, node, children):
        if self is None:
            return WizardTree(node, self, children)
        return self.children.insert(position, WizardTree(node, self, children))

    #if there are children move through them
    #if there are not any children move up a node and through the rest of those children
    def getNext(self):
        #has children
        if self.children is not None:
            #go to first child
            return self.children[0]
        #has no older siblings
        elif self.position > len(self.parent.children):
            #move to parents siblings
            return self.getNext(self.parent.key)
        #otherwise get the next oldest sibling
        return self.parent.children[self.position +1]

    #move to previous list item
    #if list is empty move up a node
    def getPrevious(self):
        #up to parent
        try:
            return self.parent.children[self.position -1]
        except IndexError:
            return self.parent



    # def fn_for_dialog(self):
    #     (...(self.key,
    #      self.value))
    #     (fn_for_lod(self.children))
    #
    # def fn_for_lod(self):
    #     if self.children is None:
    #         return None
    #     else:
    #         return (d.append(fn_for_dialog(self.children[0])),
    #          (fn_for_lod(self.children[1:]))
    #

