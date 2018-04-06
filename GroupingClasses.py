import pandas as pd
import matplotlib.pyplot as plt
import operator as op
import seaborn as sns

class TreeNode(object):
    def __init__(self, df, parent = 'head', value = None, name = 'head'):
        self.parent = parent
        self.df = df
        self.value = value  # tuple of (name, groupbyVal)
        self.table = None
        self.children = []
        self.options = None
        self.name = name

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
            self.children.append(TreeNode(self.df, self, val, name = self.name + str(i)))

    def return_children(self):
        return self.children

    def return_val(self):
        if self.parent == 'head':
            return self.value
        else:
            val = [self.value]
            par = self.parent
            #print('val,par',val, par)
            #print(par.parent)
            while par.parent != 'head':
                val += [par.value]
                par = par.parent
            return val

    def set_table(self):
        #print('here')
        opts = self.return_val()
        #print('opts', opts)
        #print(type(self.df))
        self.table = returnTable(self.df, opts)
        self.options = opts

def buildTree(df, optionList, node):

    def makeBoolChildrenVals(name, val):
        return [(name, True), (name, False)]

    def makeEpochChildrenVals(name, val):
        toRet = []
        for tup in val:
            toRet.append((name, tup))
        return toRet

    if len(optionList) > 0:
        #print('optL',optionList)
        name, val = optionList[0]

        if type(val) == bool:
            node.set_children(makeBoolChildrenVals(name, val))
        elif type(val) == tuple:
            node.set_children(makeEpochChildrenVals(name, val))
        elif type(val) == type(None):
            node.set_children([(name, None)])
        else:
            print('Error')

        for child in node.return_children():
            buildTree(child.df, optionList[1:], child)
    else:
        node.set_table()

def treeTraverse(node, func, toRet):
    if node.children != []:
        for c in node.children:
            toRet = treeTraverse(c, func, toRet)
    else:
        toRet += func(node)
        return toRet
    return toRet

def grabTables(node):
    return [(node.options, node.table)]

def countUp(node):
    return 1

def treeTables(node):
    return treeTraverse(node, grabTables, [])

def tabCounter(node):
    return treeTraverse(node, countUp, 0)

def stackCols(df):
    df.index.name = 'Rank'
    df.columns.name = 'DateRank'
    df = pd.DataFrame(df.stack(), columns = ['lst']).reset_index()

    for i, n in enumerate(['Count', 'Prop', 'AbsZ', 'pVal', 'Expected']):
        df[n] = df['lst'].apply(lambda x: x[i])

    df = df.drop(['lst'], axis = 'columns')
    return df

def unaggStackDF(tables):
    toColl = []

    def generateExp(column, spg):
        drObs = column.sum()
        exp = drObs / spg
        return[(sp, exp, drObs) for sp in column]

    for spg in tables:
        if spg < 11:
            #print(spg)
            temp = pd.DataFrame(tables[spg])
            temp.index = range(1, spg+1)

            for col in temp:
                temp[col] = generateExp(temp[col], spg)
                temp[col] = temp[col].apply(retAllAggs)

            temp = stackCols(temp)
            temp['SpG'] = spg
            toColl.append(temp)

    return pd.concat(toColl, ignore_index = True)

def aggStackDF(agg, start = 1, end = 10):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]
    for c in df:
        df[c] = df[c].apply(retAllAggs)
    df = stackCols(df)
    return df

def retAllAggs(entry):
    return [countsApply(entry), propApply(entry),
            absZScoreApply(entry), pValApply(entry), expApply(entry)]

def aggDF(agg, func, start = 1, end = 10):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]
    for c in df:
        df[c] = df[c].apply(func)
    return df

#######
#######
import scipy.stats as stats

def absZScore(obs, exp, n):
    if n == 0:
        return 0
    elif obs == exp:
        return 0
    else:
        return abs(((obs/n - exp/n)/ (((exp/n)*(1-(exp/n)))/n)**.5))

def absZScoreApply(entry):
    return absZScore(*entry)

def prop(obs, exp, n):
    if exp == 0:
        return 0
    else:
        return obs / exp
def propApply(entry):
    return prop(*entry)

def pVal(obs, exp, n):
    return stats.norm.cdf(-absZScore(obs, exp, n))
def pValApply(entry):
    return pVal(*entry)

def counts(obs, exp, n):
    return obs
def countsApply(entry):
    return counts(*entry)

def exp(obs, exp, n):
    return exp
def expApply(entry):
    return exp(*entry)
