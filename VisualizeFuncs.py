import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#####
# Given Cleaned DataFrame
# Returns a data frame with index of author names, and two columns
# one, number of species described, other with Genera described
####
def authorCounts(data):
    # Group by Genus to avoid double, triple, etc. counting
    # Index: Author name, Values: The unique author list
    GeAuths = pd.Series(data.groupby(['Genus'])['GAuthors'])
    GeAuths.index = GeAuths.map(lambda x: x[0])
    GeAuths = GeAuths.map(lambda x: x[1].iloc[0])

    #Unlist [count up] authors, name series
    SpAuths = unlistAuthors(data['SAuthors'])
    SpAuths.name = 'SpAuthored'
    GeAuths = unlistAuthors(GeAuths)
    GeAuths.name = 'GenAuthored'

    # Merge on index (with concat, ignore_index automatically = F)
    # Fill missing with 0
    toRet = pd.concat([GeAuths, SpAuths], axis = 'columns')
    toRet.fillna(0, inplace  = True)

    # Cast all numbers as int
    for c in toRet:
        toRet[c] = toRet[c].astype(int)

    return toRet

#####
# Helper function for 'authorCounts'
# Given a series of Author lists
# Returns the count of occurences
#####
def unlistAuthors(AList):
    ulAuths = []
    for lst in AList:
        for n in lst:
            ulAuths.append(n)
    ulAuths = pd.Series(ulAuths)
    ulAuths = ulAuths.value_counts()

    return ulAuths

#####
# Function for randomizing the "Rank" variable
# As a way of testing for whether or not there is structure
# in the relationship between 'DateRank', and 'Rank'
#####
def randomizeRank(data):
    dfCollector = []

    #
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

    #
    for g in data['Genus'].unique():
        work = data[data['Genus'] == g].copy()

        work = work.sort_values('Species')
        work['Rank'] = range(1,len(work)+1)

        dfCollector.append(work)

    return pd.concat(dfCollector, axis = 'rows')

#####
def speciesGrouper(data,
                    gbList = ['SpG','Rank', 'DateRank'],
                    gbListNames = ['SpG','Rank', 'DateRank']):
    split = pd.DataFrame(data.groupby(gbList)['Species'].count())
    for idx in split.index:
        for i, n in enumerate(gbListNames):
            split.loc[idx,n] = idx[i]
    split.index = range(len(split))
    return split

def tableMaker(data):
    tables = {}
    data = data.astype(int)
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


def epochSplitter(data, splitter, epochs):
    grouped = speciesGrouper(data,
                             [pd.cut(data[splitter], epochs), 'SpG', 'Rank','DateRank'],
                             ['age', 'SpG', 'Rank','DateRank'] )

    return splitToTables(grouped)

def splitToTables(data, toRet = {}):
    toRet = {}
    toSplit = [col for col in data.columns if col not in ['SpG','Rank', 'DateRank', 'Species']]
    #print(toSplit)
    if len(toSplit) > 0:
        split = toSplit[0]
        for e in data[split].unique():
            toRet[e] = splitToTables(data[data[split] == e].drop(split, axis = 'columns'), toRet)
    else:
        return tableMaker(data)

    return toRet



#####
# Totals all combinations of 'Rank', and 'DateRank'
# Also calculates "expected" number of those combinations
# return in format of {DateRank: Rank: [<observed>, <expected>, <generaTotal>]}
#####
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


#####
# Totals all combinations of 'Rank', and 'DateRank'
# Also calculates "expected" number of those combinations
# return in format of {DateRank: Rank: [<observed>, <expected>, <generaTotal>]}
#####
def speciesRankDateAgg2(tables, toIgnore = [1]):
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

def aggregator(tab):
    toRet = {}
    temp = pd.DataFrame(tab)
    spg = len(temp)
    temp.index = range(1, spg+1)

    for dRank in temp:
        toRet[dRank] = {}
        drObs = temp[dRank].sum()
        expected = drObs / spg

        for rank in temp[dRank].index:
            count = temp.loc[rank,dRank]

            toRet[dRank][rank] = [count, expected, drObs]

    return toRet


def fullAgg(df):
    return speciesRankDateAgg(
                tableMaker(
                    speciesGrouper(df)
                )
            )
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
                   'cmap': 'coolwarm_r'
               }}

def aggHeatMapper(agg,  title = '', func = propApply, center = 1, cmap = 'coolwarm', start = 1, end = 10):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]
    for c in df:
        df[c] = df[c].apply(func)
    sns.heatmap(df, annot = True, center = center,
               cmap = cmap, square = True,
               cbar = False)
    plt.title(title)

def unaggHeatMapper(tables, func = prop, norm = 2.6, center = (1/2.6), title = '', colormap = 'coolwarm'):
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

            temp[dRank] = [func(sp, exp, drObs) for sp in temp[dRank]]
            annots[dRank] = temp[dRank].copy()
            temp[dRank] = [calc/norm for calc in temp[dRank]]

        where = locs[i]
        plt.subplot2grid((23,21),(where[0]-1, where[1]-1), colspan = i, rowspan = i)
        sns.heatmap(temp, annot = annots, center = center,
                    cmap = colormap, square = True, cbar = False)

    plt.subplot2grid((23,21),(5,8), colspan = 5, rowspan = 5)
    plt.axis('equal')
    plt.axis('off')

    plt.text(-0.05,-0.01,'species Rank',
            rotation = 'vertical', fontsize = 28)
    plt.text(-0.036,-0.08,'Date Rank',
            rotation = 'horizontal', fontsize = 24)
    plt.text(0.003,-0.03,title +'\nProportion\n of\n species\n',
            fontsize = 30, horizontalalignment = 'center')

#####DEPRECATED
def epochSplitterDEP(data, splitter, epochs):
    grouped = speciesGrouper(data,
                             [pd.cut(data[splitter], epochs), 'SpG', 'Rank','DateRank'],
                             ['age', 'SpG', 'Rank','DateRank'] )
    ages = list(grouped['age'].unique())
    toRet = {}
    for a in ages:
        toRet[a] = fullTableMaker(grouped[grouped['age'] == a].drop('age', axis = 'columns'))
    return toRet

#####DEPRECATED
def speciesRankDateHeatDEP(tables, title):
    locs = {1:(1,1),2:(1,2),3:(1,4),4:(1,7),
            5:(1,11),6:(1,16),7:(7,15),8:(6,1),
            9:(15,1),10:(14,12)}

    plt.figure(figsize = (20,20))

    i = 0
    for k in tables:
        if k > 10:
            break
        i+=1

        temp = pd.DataFrame(tables[k])
        temp.index = range(1,len(temp)+1)
        annots = temp.copy()
        for c in temp:
            temp[c] = [e/temp[c].sum()/(1/len(temp)) for e in temp[c]]
            annots[c] = temp[c].copy()
            temp[c] = [e/2.6 for e in temp[c]]

        where = locs[i]
        plt.subplot2grid((23,21),(where[0]-1, where[1]-1), colspan = i, rowspan = i)
        sns.heatmap(temp, annot = annots, center = (1/2.6),
                    cmap = 'coolwarm', square = True, cbar = False)

    plt.subplot2grid((23,21),(5,8), colspan = 5, rowspan = 5)
    plt.axis('equal')
    plt.axis('off')

    plt.text(-0.05,-0.01,'species Rank',
            rotation = 'vertical', fontsize = 28)
    plt.text(-0.036,-0.08,'Date Rank',
            rotation = 'horizontal', fontsize = 24)
    plt.text(0.003,-0.03,title +'\nProportion\n of\n species\n',
            fontsize = 30, horizontalalignment = 'center')

#####DEPRECATED
# Totals all combinations of 'Rank', and 'DateRank'
# Also calculates "expected" number of those combinations
# return in format of {DateRank: Rank: [<observed>, <expected>, <generaTotal>]}
#####
def speciesRankDateAggDEP(tables):
    agg = {} # Dict to Return

    for spg in tables:
        if spg == 1: # 1 SpG is of no interest in this context
            pass

        else:
            temp = pd.DataFrame(tables[spg])
            temp.index = range(1,len(temp)+1)

            obs = temp.sum().sum()  # Aggregate observed species
            genera = obs / spg      # Genera number will be total species / SpG
            expected = genera * (1/spg)
            # expected  = genera * 1/spg for all spg
            # Actual = sum for each location.

            for dRank in temp:

                if dRank not in agg.keys():
                    agg[dRank] = {}

                for rank in temp[dRank].index:
                    count = temp.loc[rank,dRank]
                    if rank not in agg[dRank].keys():
                        agg[dRank][rank] = [0, 0, 0]

                    agg[dRank][rank][0] += count
                    agg[dRank][rank][1] += expected
                    agg[dRank][rank][2] += genera
    return agg

#####DEPRECATED
# Given data frame with 'SpG','Rank', and 'DateRank'
# returns tables that give number of species that have particular
# combination of 'SpG', 'Rank', and 'DateRank'
#####
def makeSpeciesRankDateTablesDEP(data):

    data = pd.DataFrame(data.groupby(['SpG','Rank', 'DateRank',])['Species'].count())

    # tables will have the structure:
    # {SpG: {Rank: [<list>]}}
    # The [<list>] will be the number of species that are in a genera with
    # that particular SpG, are of that Rank, and are of the DateRank
    # corresponding to the index location of the list plus 1
    tables = {}

    currentSPG = 0
    currentRank = 0
    prevDR = 0

    for idx in data.index:

        # MultiIndex in the format: (SpG, Rank, Date Rank)
        spg = idx[0]
        rank = idx[1]
        dRank = idx[2]
        sp = data.loc[idx, 'Species']

        # If the SpG changes, create new list, reset counter variables
        if spg != currentSPG:
            tables[spg] = {}
            currentSPG = spg
            tables[spg][rank] = []
            currentRank = 1
            prevDR = 0

        # If rank changes, create new list, reset dateRank counter
        if rank != currentRank:
            tables[spg][rank] = []
            currentRank = rank
            prevDR = 0

        # Check to see that current date rank is only one greater than previous
        # DateRank, if not, one was skipped, in which case zeros need to be added
        if prevDR +1 != dRank:
            for i in range(dRank-prevDR-1):
                tables[spg][rank].append(0)

        # append number of species
        tables[spg][rank].append(sp)
        prevDR = dRank

    # Check to ensure each list is properly filled
    for spg in tables:
        for rank in tables[spg]:
            while len(tables[spg][rank]) < spg:
                tables[spg][rank].append(0)

    return tables
