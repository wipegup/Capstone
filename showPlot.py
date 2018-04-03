def showPlot(source = 'real', kind = 'agg', num = 1, spgDiscard = [1], func = prop,
             AfterGenusErection = None, BeforeGenusErection = None, DuringGenusErection = None,
            Type = None, OrigGenus = None, Epoch = None, EpochType = 's'):

    def buildKeys(toRet):
        toRet = []
        blankKey = (('AfterGenusErection', []),
                    ('BeforeGenusErection', []),
                    ('DuringGenusErection', []),
                    ('Type', []),
                    ('OrigGenus', []),
                    ('Epoch', []))
        def buildKey(key, opts):

        for i, val in enumerate([AfterGenusErection, BeforeGenusErection,
                                DuringGenusErection, Type, OrigGenus, Epoch]):






    def returnGBLists():

        toGroup = ['SpG', 'Rank', 'DateRank']
        options = []
        for boolean, name in zip([AfterGenusErection, BeforeGenusErection, DuringGenusErection, Type, OrigGenus, Epoch],
                                ['AfterGenusErection', 'BeforeGenusErection', 'DuringGenusErection', 'Type', 'OrigG', 'Epoch']):
            if type(boolean) == bool:
                options = dict({name:boolean}, **options)

        toGroup.extend(list(options.keys()))
        toGroupNames = toGroup.copy()

        if Epoch:
            splitDict = {'s': 'SDate', 'g':'GDate'}
            if EpochType in splitDict.keys():
                splitter = splitDict[EpochType]
            else: # Add exception statement
                print('bad EpochType')

            if Epoch == True:
                epochs = [1758, 1815, 1916, 2020]
            else:
                epochs = Epoch
            toGroupNames.append('Epoch')
            toGroup.append(pd.cut(df[splitter], epochs))

        return toGroup, toGroupNames, options

    def returnData():
        sourceDict = {'real' : lambda x:x, 'alpha': alphaRank, 'random': randomizeRank}

        if source in sourceDict.keys():
            return sourceDict[source](df)
        else: # make exception statement
            print('Bad Source Argument')
    def makeOptionDicts():
        opts = {opt: list(grouped[opt].unique())
            for opt in gbListNames
                if opt not in ['SpG', 'Rank','DateRank']}
        def dictCompile():
            individualDicts = []

            for k in opts:
                individualDicts.append([{k:v} for v in opts[k]])

            return dictMaker(individualDicts)

        def dictMaker(lst):
            toRet = []
            for d in lst[0]:
                if len(lst)>1:
                    for ds in dictMaker(lst[1:]):
                        toRet.append(dict(d,**ds))
                else:
                    return lst[0]
            return toRet

        return dictCompile()

    def dictionaryAccessor(dct, keys):
        for k in keys: dct = dct[k]
        return dct

    def unAggPlot():
        opts = [opt for opt in gbListNames
                if opt not in ['SpG', 'Rank','DateRank']]
        tableKeys = [True] * len(opts)
        title = ' '.join(opts)
        ep = ''
        if Epoch:
            tableKeys.pop()
            ep = list(grouped['Epoch'].unique())[0]
            tableKeys.append(ep)
            title += ' of' + str(ep)
        print(dictionaryAccessor(tabs, tableKeys)[4])
        unaggHeatMapper(dictionaryAccessor(tabs, tableKeys), title = title)

    data = returnData()

    gbList, gbListNames, opts = returnGBLists()
    grouped = speciesGrouper(data, gbList = gbList, gbListNames = gbListNames)
    tabs = splitToTables(grouped)

    if kind == 'unAgg':
        unAggPlot()
    elif kind == 'Agg':
        aggPlot()
    else:
        print('unsupported plot type')


    #return tabs
    #agg = speciesRankDateAgg(tabs[True])
    #aggHeatMapper(agg)
