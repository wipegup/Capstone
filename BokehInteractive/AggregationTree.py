class TreeNode(object):

    def __init__(self, df, parent = 'head', value = ('',None), name = 'head'):
        self.parent = parent
        self.df = df
        self.value = value  # tuple of (name, groupbyVal)
        self.name = name
        self.table = None
        self.children = []
        self.opts = None

    def __repr__(self):
        return self.name

    def set_value(self, val):
        self.value = val

    def set_name(self, name):
        self.name = name

    def set_children(self, childrenVals):
        i = -1
        for val in childrenVals:
            i +=1
            self.children.append( TreeNode( self.df, self, val,
                                    name = self.name + str(i)))

    def set_opts(self):
        self.opts = self.return_options()

    def return_children(self):
        return self.children

    def return_options(self):
            if self.parent != 'head':

                n = self
                val = [n.value]
                while n.parent != 'head':
                    n = n.parent
                    val += [n.value]
                #print(val)
                return val
            else:
                print(self.value)
                return self.value

    def set_table(self):
        #print('here')
        self.set_opts()
        #print('opts', opts)
        #print(type(self.df))
        self.table = returnTable(self.df, self.opts)


def buildTree(optionList, node): # Change to class method 'Grow'?$$$$

    def makeChildrenVals(name, val):

        def makeBoolChildrenVals(name, val):
            return [(name, True), (name, False)]

        def makeListChildrenVals(name, val):
            toRet = []
            for tup in val:
                toRet.append((name, tup))
            return toRet

        if type(val) == bool:
            return makeBoolChildrenVals(name, val)
        elif type(val) == list:
            return makeListChildrenVals(name, val)
        elif type(val) == type(None):
            return [(name, None)]
        else:
            return 'Children Val Error'

    if len(optionList) > 0:
        #print('optL',optionList)
        #name, val = optionList[0]
        node.set_children( makeChildrenVals(*optionList[0]) )

        for child in node.return_children():
            buildTree(optionList[1:], child)
    else:
        node.set_table()

def leafTraverse(node, func, toRet = []):
    if node.children != []:
        for c in node.children:
            toRet = leafTraverse(c, func, toRet)
    else:
        toRet += func(node)
        return toRet
    return toRet

def grabTables(node):
    return [(node.opts, node.table)]
