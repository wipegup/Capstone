import pandas as pd
import matplotlib.pyplot as plt
import operator as op
import seaborn as sns


class TreeNode(object):
    def __init__(self, parent = 'head', value = None, name = 'head'):
        self.parent = parent
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
            self.children.append(TreeNode(self, val, name = self.name + str(i)))

    def return_children(self):
        return self.children

    def return_val(self):
        val = [self.value]
        par = self.parent

        while par.parent != 'head':
            val += [par.value]
            par = par.parent

        return val

    def set_table(self):
        opts = self.return_val()

        self.table = returnTable(df, opts)
        self.options = opts

def buildTree(optionList, node):

    def makeBoolChildrenVals(name, val):
        return [(name, True), (name, False)]

    def makeEpochChildrenVals(name, val):
        toRet = []
        for i in range(len(val)-1):
            toRet.append((name, [val[i],val[i+1]]))
        return toRet

    if len(optionList) > 0:
        name, val = optionList[0]

        if type(val) == bool:
            node.set_children(makeBoolChildrenVals(name, val))
        elif type(val) == list:
            node.set_children(makeEpochChildrenVals(name, val))
        elif type(val) == type(None):
            node.set_children([(name, None)])
        else:
            print('Error')

        for child in node.return_children():
            buildTree(optionList[1:], child)
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

##############
############
##############
def showPlot(data, source = 'real', kind = 'agg', num = 1, spgDiscard = [1], func = 'prop',
            SvGOperator = None,
            Type = None, OrigGenus = None, Epoch = None, EpochType = 's'):


    if SvGOperator:
        SDateVGDate = True
        SDateVGDateName= SvGOperator.join(['SDate ', ' GDate'])
        compDict = {'>': op.gt,'>=': op.ge,
                    '<': op.lt, '<=': op.le,'==': op.eq}
        opFunc = compDict[oper]
        data[name] = opFunc(data['SDate'], data['GDate'])
    else:
        SDateVGDateName = ''
        SDateVGDate = False

    if Epoch:
        if Epoch == True:
            Epoch = [1758, 1815, 1916, 2020]
        if EpochType == 's':
            epochCol = 'SDate'
        elif EpochType == 'g':
            epochCol = 'GDate'
        else:
            print('Error Epoch Splitter')
    else:
        epochCol = ''

    optionList = list(
                    zip(
                        [SDateVGDateName, 'Type', 'OrigG', epochCol],
                        [ SDateVGDate, Type, OrigGenus, Epoch]
                        )
                    )
    #print('init opts', optionList)
    if kind == 'unagg':
        tabs = returnTable(data, optionList)
        title = makeTitle(optionList)
        print(title)
        unaggHeatMapper(tabs, title = title, **hMapDefaults[func])

    elif kind == 'agg':
        if num == 1:
            tabs = returnTable(data, optionList)
            agg = speciesRankDateAgg(tabs, spgDiscard)
            title = makeTitle(optionList)
            print(title)
            aggHeatMapper(agg, title = title, **hMapDefaults[func])

        elif num == 'All':
            headNode = TreeNode()
            buildTree(optionList, headNode)
            #return headNode
            numFigs = tabCounter(headNode)
            dim = int(numFigs** .5) if (numFigs**.5).is_integer() else (int(numFigs **.5)+1)
            tables = treeTables(headNode)
            plt.figure(figsize = (20,20))

            i = 0
            for ele in tables:
                i += 1
                plt.subplot(dim, dim, i)
                opts, tabs = ele
                title = makeTitle(opts)
                print(title)
                aggHeatMapper(speciesRankDateAgg(tabs, spgDiscard), title = title, **hMapDefaults[func])
            plt.tight_layout()
        else:
            print('Error, num argument')

##############
##############
############

def optionParse(options, starter, boolFunc, listFunc):
    toRet = starter
    for e in options:
        name, val = e

        if type(val) == type(None):
            pass

        elif type(val) == bool:
            toRet = boolFunc(name, val, toRet)

        elif type(val) == list:
            toRet = listFunc(name, val, toRet)
        else:
            print('Error', type(val))

    return toRet

def makeTitle(options):

    def titleBool(name, val, toRet):
        if val: toRet += ' ' + str(name) + ' '
        else: toRet += ' Not ' + str(name) + ' '
        return toRet

    def titleList(name, val, toRet):
        toRet += ' Epoch ' + str(val[0]) + ' to ' + str(val[1]) + ' '
        return toRet

    return optionParse(options, '', titleBool, titleList)


def returnTable(data, options = []):
    def makeMask(options):
        def maskBool(name, val, toRet):
            toRet = toRet & (data[name] == val)
            return toRet

        def maskList(name, val, toRet):
            toRet = toRet & ((data[name] >= val[0])& (data[name] < val[1]))
            return toRet

        return optionParse(options, True, maskBool, maskList)

    mask = makeMask(options)
    if type(mask) != bool:
        data = data[mask]
    return tableMaker(speciesGrouper(data))

def speciesGrouper(data):
    gbList = ['SpG','Rank', 'DateRank']
    split = pd.DataFrame(data.groupby(gbList)['Species'].count())
    split = split.reset_index()

    return split

def tableMaker(data):
    tables = {}
    for row in data.iterrows():

        sp = row[1]['Species']
        spg = row[1]['SpG']
        rank = row[1]['Rank']
        dRank = row[1]['DateRank']

        if spg not in tables.keys():
            tables[spg] = {}

        if rank not in tables[spg].keys():
            tables[spg][rank] = [0] * spg

        if tables[spg][rank][dRank-1] == 0:
            tables[spg][rank][dRank-1] = sp
        else:
            print('error', spg, rank, dRank)

    for k in tables:
        for i in range(1, k+1):
            if i not in tables[k].keys():
                tables[k][i] = [0]*k
    return tables




##################
#################
##############
#################
def speciesRankDateAgg(tables, toIgnore = [1]):
    agg = {} # Dict to Return

    for spg in tables:
        if spg in toIgnore:
            pass

        else:
            temp = pd.DataFrame(tables[spg])
            temp.index = range(1,len(temp)+1)

            for dRank in temp:
                drObs = temp[dRank].sum()
                expected = drObs /spg

                if dRank not in agg.keys():
                    agg[dRank] = {}

                for rank in temp[dRank].index:
                    count = temp.loc[rank,dRank]
                    if rank not in agg[dRank].keys():
                        agg[dRank][rank] = [0, 0, 0]

                    agg[dRank][rank][0] += count
                    agg[dRank][rank][1] += expected
                    agg[dRank][rank][2] += drObs
    return agg

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
    return stats.norm.cdf(-absZScoreApply(*entry))

def counts(obs, exp, n):
    return obs
def countsApply(entry):
    return counts(*entry)
'''
hMapDefaults = { 'prop':{
                'func' : propApply,
                'center':1,
                'cmap' : 'coolwarm'},
               'z':{
                   'func' : absZScoreApply,
                   'center':1.64,
                   'cmap':'coolwarm'},
               'pVal':{
                   'func': pValApply,
                   'center': .10,
                   'cmap': 'coolwarm_r'},
                'count':{
                    'func':countsApply,
                    'center': 0,
                    'cmap': 'coolwarm'
                }
               }
def aggHeatMapper(agg,  title = '', func = propApply, center = 1, cmap = 'coolwarm', start = 1, end = 10):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]
    for c in df:
        df[c] = df[c].apply(func)
    sns.heatmap(df, annot = True, center = center,
               cmap = cmap, square = True,
               cbar = False)
    plt.title(title)

def unaggHeatMapper(tables, func = prop, norm = 2.6, center = (1/2.6), title = '', cmap = 'coolwarm'):
    locs = {1:(1,1), 2:(1,2), 3:(1,4), 4:(1,7),
            5:(1,11), 6:(1,16), 7:(7,15), 8:(6,1),
            9:(15,1), 10:(14,12)}

    plt.figure(figsize = (20,20))

    i = 0
    for spg in tables:
        if spg > 10:
            break
        i+=1

        temp = pd.DataFrame(tables[spg])
        temp.index = range(1,spg+1)
        annots = temp.copy()
        for dRank in temp:
            drObs = temp[dRank].sum()
            exp = drObs / spg

            temp[dRank] = [func((sp, exp, drObs)) for sp in temp[dRank]]
            annots[dRank] = temp[dRank].copy()
            temp[dRank] = [calc/norm for calc in temp[dRank]]

        where = locs[i]
        plt.subplot2grid((23,21),(where[0]-1, where[1]-1), colspan = i, rowspan = i)
        sns.heatmap(temp, annot = annots, center = center,
                    cmap = cmap, square = True, cbar = False)

    plt.subplot2grid((23,21),(5,8), colspan = 5, rowspan = 5)
    plt.axis('equal')
    plt.axis('off')

    plt.text(-0.05,-0.01,'species Rank',
            rotation = 'vertical', fontsize = 28)
    plt.text(-0.036,-0.08,'Date Rank',
            rotation = 'horizontal', fontsize = 24)
    plt.text(0.003,-0.03,title +'\nProportion\n of\n species\n',
            fontsize = 30, horizontalalignment = 'center')
'''
