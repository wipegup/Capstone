'''source:{'Real':'real','Alphabetized':'alpha','Random':'rand'}
kind:{'Aggregated':'agg', 'Unaggregated':'unagg'}
func:{'Proportion':'Prop', 'Absolute z-score':'AbsZ', 'p-Value':'pVal', 'Count':'Count'}
Tspecies:['No Split','True', 'False', 'Both']
SpVG:['None', '>','>=','<','<=','==','!=']
OGenus:['No Split','True','False','Both']
epochControls['OnOff']:[True,False]
epochControls[i]['beg']:int
epochControls[i]['end']:int
epochControls[i]['check']:[True,False]'''
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

def replot(b):
    with open('df.pickle', 'rb') as f:
        df = pickle.load(f)
    def getData(source):
        retFunc = {'real': lambda x:x,
                    'alpha':alphaRank,
                    'rand':randomizeRank}
        return retFunc[source](df)

    def getPlotOpts(df, typeS, OrigGenus, SpVG, epochControls):

        def SVGComparison(df, oper):
            if oper:
                name = oper.join(['SDate ', ' GDate'])
                compDict = {'>': op.gt,'>=': op.ge,
                            '<': op.lt, '<=': op.le,'==': op.eq}
                opFunc = compDict[oper]
                df[name] = opFunc(df['SDate'], df['GDate'])
                return df, name, True
            else:
                return df, '', None

        df, SVGName, SVGAct = SVGComparison(df, SpVG)
        epochDates = []
        if epochControls['OnOff'].value:
            epochColDict = { 's':'SDate', 'g':'GDate'}
            epochCol = epochColDict[epochControls['Kind'].value]
            for i in range(1,4):
                work = epochControls[i]
                if work['check']:
                    epochDates.append((work['beg'].value,work['end'].value))
        else:
            epochCol = ''
            epochDates = None

        optionsList = list(
                            zip([SVGName, 'Type', 'OrigG', epochCol],
                                [SVGAct, typeS, OrigGenus, epochDates]

                            )
                        )
        return df, optionsList

    df = getData(source.value)

    df, plotOpts = getPlotOpts(df, Tspecies.value,
                    OGenus.value, SpVG.value, epochControls)

    passFunc = func.value
    if kind.value:
        disp = aggDisplay(df, passFunc, plotOpts)
    else:
        disp = unaggDisplay(df, passFunc, plotOpts)
    #clear_output()
    show(disp)
