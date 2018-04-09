from IPython.display import display, clear_output
from bokeh.io import show, push_notebook
exec(open('./BokehInteractive/BackendFunctions.py').read())
exec(open('./BokehInteractive/GroupingFuncs.py').read())
exec(open('./BokehInteractive/AggregationTree.py').read())
#exec(open('.temp.py').read())
exec(open('./BokehInteractive/BokehFuncs.py').read())
exec(open('./BokehInteractive/ControlWidgets.py').read())

try:
    with open('./data/df.pickle', 'rb') as f:
        df = pickle.load(f)
except:
    print('scraping Data')
    exec(open('./data/Data.py').read())

def makeWidgetValueDict():

    def getData(source):
        retFunc = {'real': lambda x:x,
                    'alpha': alphaRank,
                    'rand': randomizeRank}

        with open('./data/df.pickle', 'rb') as f:
            df = pickle.load(f)

        return retFunc[source](df)

    data = getData(source.value)

    SpVGName = ''

    if SpVG.value:
        oper = SpVG.value
        compDict = {'>': op.gt,'>=': op.ge,
                    '<': op.lt, '<=': op.le,'==': op.eq}
        opFunc = compDict[oper]

        SpVGName = oper.join(['SDate ', ' GDate'])
        data[SpVGName] = opFunc(data['SDate'], data['GDate'])

    commonDict = {
        'data': data,
        'func': func.value,
        'SpVGName' : SpVGName,
        'epochCol' : epochKind.value
    }

    def buildEpochList():
        epochDates = []
        if epochControls['OnOff'].value:
            for i in range(1,4):
                work = epochControls[i]
                if work['check'].value:
                    epochDates.append((work['beg'].value,work['end'].value))
        else:
            epochDates = None
        return epochDates

    def buildToIgnore():
        toIgnore = []
        for k in spgSelector:
            if type(k) == int:
                if spgSelector[k].value:
                    if k > 10:
                        toIgnore.extend(list(range(k, 91)))
                    else:
                        toIgnore.append(k)

        if spgSelector['which'].value:
            toIgnore = [i for i in range(1,91) if i not in toIgnore ]

        return toIgnore

    agg = {
        'OrigG': AOGenus.value,
        'Type': ATspecies.value,
        'epochList' : buildEpochList(),
        'SVGChooser': SVGChooser.value if SpVGName != '' else None,
        'start': startEnd.lower,
        'end': startEnd.upper,
        'toIgnore' : buildToIgnore(),
        }

    def UAEpoch():
        if UAEpochCheck.value:
            return (UAEStart.value, UAEEnd.value)
        else:
            return None

    unagg = {
        'OrigG': UAOGenus.value,
        'Type': UATspecies.value,
        'epochList': UAEpoch(),
        'SVGChooser': True if SpVGName != '' else None
        }

    toRet = {}
    toRet['agg'] = dict(**agg, **commonDict)
    toRet['unagg'] = dict(**unagg, **commonDict)

    return toRet

def replot(b):
    tabDict = {0: 'agg', 1: 'unagg'}
    plotType = tabDict[kind.selected_index]

    wDict = makeWidgetValueDict()[plotType]

    optionsList = list( zip(
        ['OrigG', 'Type', wDict['SpVGName'], wDict['epochCol']],
        [wDict['OrigG'], wDict['Type'], wDict['SVGChooser'], wDict['epochList']]
        ))

    if plotType == 'agg':
        aggSubgrouping = {key:wDict[key] for key in ['start','end','toIgnore']}
        #print('this')
        disp = aggDisplay(wDict['data'], wDict['func'], optionsList, **aggSubgrouping)
        #print('that')
    elif plotType == 'unagg':

        disp = unaggDisplay(wDict['data'], wDict['func'], optionsList)
    #print('there')
    clear_output()
    show(disp)

class IPlot(object):
    def __init__(self):
        p = figure(title = 'Press "Replot" button for selected visual')
        p.title.text_font_size = "25px"
        self.layout = layout(p)
        self.handle = show(l)

    def replot(self):
        pass

def Interact():
    replotButton.on_click(replot) # Replot Function from BokehReplotting.py
    #p = figure(title = 'Press "Replot" button for selected visual')
    #p.title.text_font_size = "25px"
    #l = layout(p)
    display(kind)
    #handle = show(l)

#####
# Testing Functions
#####
def printDict(b):
    wd = makeWidgetValueDict()
    for k in wd:
        if type(wd[k]['data']) == type(pd.DataFrame()):
            wd[k]['data'] = 'df'
        else:
            wd[k]['data'] = 'error'

    print(wd)

def widgetTest():
    display(kind)
    replotButton.on_click(printDict)
