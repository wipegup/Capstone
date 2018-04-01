#####
# Script used to find best fitting Decision Tree
#####

## Imports

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
import pickle
import time
with open('df.pickle', 'rb') as f:
        df = pickle.load(f)

#####
# crossVal helper method returns fit-scores for models fit on each
# fold for cross-validation.
#####
def crossVal(clf, X, y, folds = 3):

    scores = [] # container to return
    randOrd = np.random.permutation(len(y)) # permutes range of df range
    slices = list(range(0,len(y)+1, int(len(y)/folds))) # NEED TO REFACTOR

    foldIndex = [randOrd[slice(slices[i],slices[i+1])] for i in range(folds) ]

    for tfi in foldIndex:
        y_test = y.loc[tfi]
        X_test = X.loc[tfi]

        notTfi = [fi for fi in foldIndex if (fi != tfi).any() ] # comparing two lists
        train = [item for sublist in notTfi for item in sublist] # unpacking indexes in the not testing groups
        y_train = y.loc[train]
        X_train = X.loc[train]

        clf.fit(X_train, y_train)

        scores.append(clf.score(X_test, y_test))

    return scores

#####
# searcher takes a dictionary of targets, features stored in X, and a dictionary
# of parameters for DecisionTreeRegressor
# Returns dictionary of times and scores
#####
def searcher(targetDict, X, paramDict):
    toRet = []

    for targetName in targetDict:
        targTime0 = time.time()
        print(targetName)

        toTry = dictCompile(paramDict)
        for argDict in toTry:
            print(argDict)

            t0 = time.time()
            scores = crossVal(DecisionTreeRegressor(**argDict),
                    X,
                    targetDict[targetName],
                    100)

            t1 = time.time()
            name = dict({'name':str(DecisionTreeRegressor).split('.')[-1][:-2]},
                        **argDict)

            toRet.append((name, np.mean(scores), np.std(scores), t1-t0))
        print(time.time() - targTime0)

    return toRet

#####
# dictCompile takes in a dictionary such as would be passed to GridSearchCV
# in the format of {'<paramname>'': [<param1>,<param1a>,...]}
# returns dictionaries that can be passed into regressors of the format
# {'<paramname>':<param1>, '<paramname2>':<param2}
#####
def dictCompile(funcDict):
    individualDicts = []

    for k in funcDict:
        individualDicts.append([{k:v} for v in funcDict[k]])

    return dictMaker(individualDicts)

#####
# helper function to build out param dictionaries
# recursive magic
####
def dictMaker(lst):
    toRet = []
    for d in lst[0]:
        if len(lst)>1:
            for ds in dictMaker(lst[1:]):
                toRet.append(dict(d,**ds))
        else:
            return lst[0]
    return toRet

with open('df.pickle', 'rb') as f:
        df = pickle.load(f)
df = df[df['SpG'] != 1]

df.index = range(0, len(df))

stdTarget = (df['Rank']-1) / df['SpG']
rawTarget = df['Rank']
logTarget = np.log(df['Rank'])

targetDict = {'std':stdTarget, 'raw': rawTarget, 'log':logTarget}

tofit = ['DateRank', 'SpG']
X = df[tofit]
X['Interaction'] = X['DateRank'] * X['SpG']

parameters = {
'max_depth': range(2,41,2),
'min_samples_split': range(2,10),
'min_samples_leaf': range(1,5),
'criterion': ['mse','mae','friedman_mse'],
'splitter': ['best','random']
}

def doit():
    t0 = time.time()
    l = searcher(targetDict, X, parameters)
    t1 = time.time()

    print('total', t1-t0)

    return l

mods = doit()
with open('searched.pickle', 'wb') as f:
    pickle.dump(mods, f, protocol = 0)
