import pandas as pd
import matplotlib.pyplot as plt
import operator as op
import seaborn as sns

#####DEPRECATED
hMapDefaults = { 'Prop':{
                'func' : propApply,
                'center':1,
                'cmap' : 'coolwarm', 'norm' : 2.6},
               'AbsZ':{
                   'func' : absZScoreApply,
                   'center':1.64,
                   'cmap':'coolwarm'},
               'pVal':{
                   'func': pValApply,
                   'center': .10,
                   'cmap': 'coolwarm_r'},
                'Count':{
                    'func':countsApply,
                    'center': 0,
                    'cmap': 'coolwarm'
                }
               }


##############DEPRECATED
############
############## DEPRECIATED
def showPlot(data, source = 'real', kind = 'agg', num = 1, spgDiscard = [1], func = 'Prop',
             SDateVGDate = None, SGvsOperator = '>',
            Type = None, OrigGenus = None, Epoch = None, EpochType = 's'):

    def SVGComparison(oper):
        name = oper.join(['SDate ', ' GDate'])
        compDict = {'>': op.gt,'>=': op.ge,
                    '<': op.lt, '<=': op.le,'==': op.eq}
        opFunc = compDict[oper]
        data[name] = opFunc(data['SDate'], data['GDate'])
        return data, name
    SDateVGDateName = ''
    if type(SDateVGDate) == bool:
        data, SDateVGDateName  = SVGComparison(SGvsOperator)

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
    print('init opts', optionList)
    if kind == 'unagg':
        tabs = returnTable(data, optionList)
        title = makeTitle(optionList)
        print(title)
        unaggHeatMapper(tabs, title = title, **hMapDefaults[func])

    elif kind == 'agg':
        plt.figure(figsize = (8,8))
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

def aggHeatMapper(agg,  title = '', func = propApply, center = 1, cmap = 'coolwarm', start = 1, end = 10, norm = 0):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]
    for c in df:
        df[c] = df[c].apply(func)
    sns.heatmap(df, annot = True, center = center,
               cmap = cmap, square = True,
               cbar = False)
    plt.title(title)

def unaggHeatMapper(tables, func = propApply, norm = 2.6, center = (1/2.6), title = '', cmap = 'coolwarm'):
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
        sns.heatmap(temp, annot = annots, center = center/norm,
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
