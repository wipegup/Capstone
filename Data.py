import requests
from bs4 import BeautifulSoup
import pandas as pd

response = requests.get('http://www.worldbirdnames.org/master_ioc-names_xml.xml')
soup = BeautifulSoup(response.text, 'xml')
print(response.status_code)

speciesTree = []
for o in soup.find_all('order'):
    oname = o.find('latin_name').text
    for f in o.find_all('family'):
        fname = f.find('latin_name').text
        for g in f.find_all('genus'):
            gname = g.find('latin_name').text
            gAuthority = g.find('authority').text
            rank = 0
            for s in g.find_all('species'):
                rank +=1
                sname = s.find('latin_name').text
                toApp = [rank, oname, fname, gname, sname, gAuthority, s.find('authority').text, s.find('breeding_regions').text]
                speciesTree.append(toApp)

#####
# Cleaning
#####

def cleanNames(nameCol):
    toRet = []
    for n in nameCol:
        #print(n)
        n = n.replace(',', '')
        n = n.replace('& ', '')
        n = n.replace('et al', 'EtAl')
        n = n.strip()
        #print(n)
        toRet.append(n)
    return toRet
df = pd.DataFrame(speciesTree)
df.columns = ['Rank', 'Order', 'Family','Genus','Species','GAuth','SAuth','BreedRegion']

df['OrigG'] = [a.count(')') == 0 for a in df['SAuth']]
df['SAuth'] = df['SAuth'].str.replace( ')', '')
df['SAuth'] = df['SAuth'].str.replace( '(', '')

df['SDate'] = [int(a[-4:]) for a in df['SAuth']]
df['SAuthors'] = [ a[:-4] for a in df['SAuth']]

df['GDate'] = [int(a[-4:]) if a != 'E' else 1816 for a in df['GAuth'] ]
df['GAuthors'] = [a[:-4] if a != 'E' else 'Vieillot' for a in df['GAuth']]

df['SAuthors'] = cleanNames(df['SAuthors'])
df['GAuthors'] = cleanNames(df['GAuthors'])
df['BreedRegion'] = cleanNames(df['BreedRegion'])

df = df.drop(['GAuth','SAuth'], axis = 'columns')
df['DateRank'] = df.groupby('Genus')['SDate'].rank(ascending = True, method = 'min').astype(int)
#df['FullName'] = df['Order'] +' '+ df['Family']+' ' + df['Genus']+'_' + df['Species'].str[:-2]

spg = df.groupby('Genus')['Species'].count()
spg.name = 'SpG'

raw = df.merge(pd.DataFrame(spg), left_on= 'Genus', right_index= True)
raw.to_csv('SpGOrig.csv')

def addToNameDict(wds,MWNameDict):
    if len(wds) == 0:
        return None
    else:
        if wds[0] in MWNameDict:
            toPass = MWNameDict[wds[0]]

        else:
            toPass = {}
        MWNameDict[wds[0]] = addToNameDict(wds[1:], toPass)
        return MWNameDict

multiWordNames = ['zu Wied-Neuwied', 'Meyer de Schauensee', 'Barboza du Bocage',
                 'de Sélys-Longchamps', 'Du Bus de Gisignies',
                 'Gurney Sr', 'de Sparre', 'Gurney Jr',
                 'Xántus de Vésey', 'Da Silva Maia', 'de la Llave',
                 'de Filippi', 'Phelps Jr', 'Cardoso da Silva Novaes',
                 'Wetmore Phelps Jr', 'Giraud Jr', 'De Vis',
                 'De Roo', 'La Touche', 'Marshall JT Jr',
                 'de Tarragon', 'Phelps Jr', 'Le Maout',
                 'Raposo do Amaral']
MWND = {}
for n in multiWordNames:
    MWND = addToNameDict(n.lower().split(' '), MWND)

def authorSplit(ent):
    lst=[]
    spt = ent.split(' ')
    i = 0
    while i < len(spt):
        increment = 1

        if spt[i].isupper():
            prev = lst.pop()
            lst.append(' '.join([prev, spt[i]]).lower())

        elif (len(spt[i:])>1)&(spt[i].lower() in MWND):
            long = longName(spt[i:])
            lst.append(long)
            increment = len(long.split(' '))

        else:
            lst.append(spt[i].lower())
        i+=increment
    return lst

def longName(nList):
    #print(nList)
    toRet = []
    more = MWND.copy()

    j = 0
    while more:

        toRet.append(nList[j].lower())
        if nList[j].lower() in more:
            more = more[nList[j].lower()]
        else:
            if j == 1:
                return nList[0]
            else:
                print('no')

        j+=1
    #print(' '.join(toRet))
    return ' '.join(toRet)

df = raw.copy()
df['SAuthors'] = df['SAuthors'].apply(authorSplit)
df['GAuthors'] = df['GAuthors'].apply(authorSplit)

import pickle
with open('df.pickle', 'wb') as f:
    pickle.dump(df, f, protocol=0)
