import numpy as np
import pandas as pd

def optionParse(options, starter, boolFunc, listFunc):
    toRet = starter
    for e in options:
        name, val = e

        if type(val) == type(None):
            pass

        elif type(val) == bool:
            toRet = boolFunc(name, val, toRet)

        elif type(val) == tuple:
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
    if type(options) == type(None):
        return 'All'
    else:
        return optionParse(options, '', titleBool, titleList)

def returnTable(data, options = []):
    def makeMask(options):
        def maskBool(name, val, toRet):
            toRet = toRet & (data[name] == val)
            return toRet

        def maskList(name, val, toRet):
            toRet = toRet & ((data[name] >= val[0])& (data[name] < val[1]))
            return toRet
        if type(options) == type(None):
            return True
        else:
            return optionParse(options, True, maskBool, maskList)

    def speciesGrouper(data):
        gbList = ['SpG','Rank', 'DateRank']
        split = pd.DataFrame(data.groupby(gbList)['Species'].count())
        split = split.reset_index()

        return split

    mask = makeMask(options)
    if type(mask) != bool:
        data = data[mask]
    return tableMaker(speciesGrouper(data))

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
