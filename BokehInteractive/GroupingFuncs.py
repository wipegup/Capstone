def stackCols(df):
    df.index.name = 'Rank'
    df.columns.name = 'DateRank'
    df = pd.DataFrame(df.stack(), columns = ['lst']).reset_index()

    for i, n in enumerate(['Count', 'Prop', 'AbsZ', 'pVal', 'Expected']):
        df[n] = df['lst'].apply(lambda x: x[i])

    df = df.drop(['lst'], axis = 'columns')
    return df

def stringRankings(df):
    df['Rank'] = df['Rank'].astype(str)
    df['DateRank'] = df['DateRank'].astype(str)
    return df

def unaggStackDF(tables):

    toColl = []
    for spg in tables:
        if spg < 11:
            #print(spg)
            temp = pd.DataFrame(tables[spg])
            temp.index = range(1, spg+1)

            for col in temp:
                temp[col] = generateExp(temp[col], spg)
                temp[col] = temp[col].apply(retAllCalc)

            temp = stackCols(temp)
            temp['SpG'] = spg
            toColl.append(temp)

    toRet = pd.concat(toColl, ignore_index = True)

    return stringRankings(toRet)

def aggStackDF(agg, start = 1, end = 10):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]

    for c in df:
        df[c] = df[c].apply(retAllCalc)

    df = stackCols(df)
    return stringRankings(df)

import scipy.stats as stats
def retAllCalc(entry):

    def absZScore(obs, exp, n): # Are the "zero" cases reasonable?
        if n == 0:
            return 0
        elif obs == exp:
            return 0
        else:
            return abs(((obs/n - exp/n)/ (((exp/n)*(1-(exp/n)))/n)**.5))

    def prop(obs, exp, n):
        if exp == 0:
            return 0
        else:
            return obs / exp

    def pVal(obs, exp, n):
        return stats.norm.cdf(-absZScore(obs, exp, n))

    def counts(obs, exp, n): # Remove? replace with entry[0]?
        return obs

    def exp(obs, exp, n): # Remove? replace with entry[1]?
        return exp

    return [counts(*entry), prop(*entry),
            absZScore(*entry), pVal(*entry), exp(*entry)]


#####DEPRECATED
def aggDFDEP(agg, func, start = 1, end = 10):
    df = pd.DataFrame(agg)
    df = df.loc[start:end, start:end]
    for c in df:
        df[c] = df[c].apply(func)
    return df
