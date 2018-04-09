import numpy as np
import pandas as pd

def optionParse(options, starter, boolFunc, tupFunc):
    toRet = starter
    for e in options:
        name, val = e
        #print(name, val)
        if type(val) == type(None):
            #print('pass')
            pass

        elif type(val) == bool:
            #print('bool')
            toRet = boolFunc(name, val, toRet)

        elif type(val) == tuple:
            #print('tup')
            toRet = tupFunc(name, val, toRet)
        else:
            print('Error', type(val))
    #print(toRet)
    return toRet

def returnTitle(options):

    def titleBool(name, val, toRet):
        if val: toRet += ' ' + str(name) + ' '
        else: toRet += ' Not ' + str(name) + ' '
        return toRet

    def titleTup(name, val, toRet):
        toRet += ' Epoch ' + str(val[0]) + ' to ' + str(val[1]) + ' '
        return toRet

    if type(options) == type(None):
        return 'All'
    else:
        return optionParse(options, '', titleBool, titleTup)

def returnTable(data, options = []):
    #print(options)
    def returnMask(data,options):
        #print(options)
        def maskBool(name, val, toRet):
            toRet = toRet & (data[name] == val)
            return toRet

        def maskTup(name, val, toRet):
            #print(name, val[0], val[1], toRet)
            #print(((data[name] >= val[0]) & (data[name] < val[1])))
            toRet = toRet & ((data[name] >= val[0]) & (data[name] < val[1]))
            return toRet

        toRet =  optionParse(options, [True] * len(data), maskBool, maskTup)

        if type(toRet) == bool:
            return [True] * len(data)
        else:
            return toRet

    def tableMaker(data):

        def speciesGrouper(data):
            gbList = ['SpG','Rank', 'DateRank']
            split = pd.DataFrame(data.groupby(gbList)['Species'].count())
            split = split.reset_index()

            return split

        def filltables(tables):
            for spg in tables:
                for rank in range(1, spg+1):
                    if rank not in tables[spg].keys():
                        tables[spg][rank] = [0]*spg
            return tables

        data = speciesGrouper(data)
        tables = {}

        for row in data.iterrows():

            sp = row[1]['Species']
            spg = row[1]['SpG']
            rank = row[1]['Rank']
            dRank = row[1]['DateRank']

            if spg not in tables.keys():
                tables[spg] = {}

            work = tables[spg]

            if rank not in work.keys():
                work[rank] = [0] * spg

            work = work[rank]
            if work[dRank-1] == 0:
                work[dRank-1] = sp
            else:
                print('error', spg, rank, dRank)

        return filltables(tables)

    mask = returnMask(data, options)
    data = data[mask]
    return tableMaker(data)

def generateExp(column, spg):
    drObs = column.sum() # Date Rank observations
    exp = drObs / spg
    return[(sp, exp, drObs) for sp in column]

def speciesRankDateAgg(tables, toIgnore = [1]):
    agg = {} # Dict to Return

    for spg in tables:
        if spg in toIgnore: pass

        else:
            temp = pd.DataFrame(tables[spg])
            temp.index = range(1, len(temp)+1)

            for dRank in temp:

                if dRank not in agg.keys():
                    agg[dRank] = {}

                temp[dRank] = generateExp(temp[dRank], spg)
                dRankCol = temp[dRank]

                for rank in dRankCol.index:
                    if rank not in agg[dRank].keys():
                        agg[dRank][rank] = [0, 0, 0]

                    agg[dRank][rank] = [sum(x)
                                        for x in
                                        zip(agg[dRank][rank], dRankCol[rank])]

    return agg

#####
# Function for randomizing the "Rank" variable
# As a way of testing for whether or not there is structure
# in the relationship between 'DateRank', and 'Rank'
#####
def randomizeRank(data):
    dfCollector = []

    for g in data['Genus'].unique():
        work = data[data['Genus'] == g].copy()

        work['Rank'] = np.random.permutation(range(1,len(work)+1))
        dfCollector.append(work)

    return pd.concat(dfCollector, axis = 'rows')

#####
# Function for assigning rank by alphabetical order,
# as a way of testing for structure in relationship between
# 'DateRank', and 'Rank'
#####
def alphaRank(data):
    dfCollector = []

    for g in data['Genus'].unique():
        work = data[data['Genus'] == g].copy()

        work = work.sort_values('Species')
        work['Rank'] = range(1,len(work)+1)

        dfCollector.append(work)

    return pd.concat(dfCollector, axis = 'rows')
