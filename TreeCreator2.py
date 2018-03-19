import numpy as np
def simTree(generaNum, generations, split = .001, diffDist = np.random.normal, diffThresh = 2, starterVal = [0]):
    np.random.seed(1738)
    genera = [starterVal for i in range(generaNum)]

    for c in range(generations):
        #print(genera)
        for i, g in enumerate(genera):
            toAddInit = []
            toAddFin = []
            for sp in g:
                if np.random.uniform() < split:

                    potentialS = diffDist(sp)
                    #print(potentialS)
                    different = True
                    for s in g:
                        #print(abs(s-potentialS))
                        if abs(s-potentialS) < diffThresh:
                            #print('here')
                            different = False
                            break

                    if different:
                        toAddInit.append(potentialS)

            #print(toAddInit)
            if len(toAddInit) >1:
                for idx, pot in enumerate(toAddInit):
                    toAdd = True
                    for idx2 in range(idx, len(toAddInit)):
                        if abs(toAddInit[idx2] - pot) < diffThresh:
                            toAdd = False
                            break
                    if toAdd:
                        toAddFin.append(pot)
            else:
                toAddFin = toAddInit
            if toAddFin != []:
                #print('here2')
                toRep = g.copy()
                toRep.extend(toAddFin)
                genera[i] = toRep

    return genera

import pickle
import time
spParams =np.logspace(-1,-10)
diffTParam = np.linspace(.5,2.5)
toRet = []
i = 0

for sp in spParams:
    for dtP in diffTParam:
        i+=1
        t0 = time.time()
        print(dtP, sp, i)
        st = simTree(2000, 1000, split = sp, diffThresh= dtP)
        toRet.append((sp, dtP, [len(e) for e in st]))
        print((time.time()-t0)/60)

with open('toRet2.pickle','wb') as f:
    pickle.dump(toRet,f, protocol = 0)
