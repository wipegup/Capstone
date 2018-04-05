from matplotlib.colors import rgb2hex
from matplotlib.pyplot import get_cmap
from bokeh.models import LogColorMapper, Spacer, LabelSet

cw = get_cmap('coolwarm')
cwr = get_cmap('coolwarm_r')

cw = [rgb2hex(cw(i)[:3]) for i in range(256)]
cwr = [rgb2hex(cwr(i)[:3]) for i in range(256)]

#pVallinearColorMaps =
#x = [1, 64, 128, 192, 256]
#y = [0,.01, .05, .1, .5]

funcDict = { 'Prop':{
                'func' : propApply,
                'center':1,
                'cmap' : 'coolwarm',
                'colors': cw,
                'cmapper':LinearColorMapper},
           'AbsZ':{
               'func' : absZScoreApply,
               'center':1.64,
               'cmap':'coolwarm',
               'colors': cw,
               'cmapper':LinearColorMapper},
           'pVal':{
               'func': pValApply,
               'center': .10,
               'cmap': 'coolwarm_r',
               'colors': cwr,
               'cmapper':LogColorMapper},
            'Count':{
                'func':countsApply,
                'center': 0,
                'cmap': 'coolwarm',
                'colors': cw,
                'cmapper':LinearColorMapper}
           }


defaultFigKW = {'plot_width': 400, 'plot_height':400,
                'tools': "hover,save,pan,box_zoom,reset,wheel_zoom",
                'x_axis_location' : 'above', 'toolbar_location' : None}


def buildUnaggFigDict(x):
    toRet = {}
    for i in range(1,11):
        toRet[i] = {'plot_width':i*x, 'plot_height':i*x,'tools' : 'hover',
                'x_axis_location' : 'above', 'toolbar_location' : None}
    toRet['MidSpacer'] = {'width':6*x, 'height':6*x}
    toRet['BotSpacer'] = {'width':2*x, 'height':2*x}
    return toRet

def setPlotStyle(p):
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = '10pt'
    p.axis.major_label_standoff = 0

    return p

def addLabelToDF(df):
    df.loc[:,'labelText'] = [round(e,1) for e in df.loc[:,func]]
    return df

def calcColRange(df, func, center):
    realMin, realMax = df[func].min(), df[func].max()
    maxSpread = np.max([center - realMin, realMax -center])
    return center-maxSpread , center + maxSpread


def unaggDisplay(df, func, plotOpts = []):
    plotOpts = [(e[0], None) if e[1] == 'Both' ## Check?
                else e for e in plotOpts]
    tabs = returnTabe(df, plotOpts)
    title = makeTitle(plotOpts)
    unaggFigDict = buildUnaggFigDict(45)

    return returnUnaggDisplay(tabs, func, unaggFigDict)

def returnUnaggDisplay(tabs, func = 'Prop', unaggFigDict):
    df = unaggStackDF(tabs)
    df['Rank'] = df['Rank'].astype(str)
    df['DateRank'] = df['DateRank'].astype(str)
    low, high = calcColRange(df,func, funcDict[func]['center'])

    def unaggPlot(df, spg, func, unaggFigDict):

        colors = funcDict[func]['colors']
        mapper = funcDict[func]['cmapper'](palette = colors, low = low, high = high)
        df = addLabelToDF(df)

        source = ColumnDataSource(df)
        x_range = [str(n) for n in range(1, spg + 1)]
        y_range = list(reversed(x_range.copy()))
        p = figure(title = '', x_range = x_range, y_range = y_range, **unaggFigDict[spg])
        p = setPlotStyle(p)

        p.rect( x = 'DateRank', y = 'Rank', width = 1, height = 1,
                source = source, dilate = True,
                fill_color = {'field': func, 'transform': mapper},
                line_color = None)

        labels = LabelSet(x = 'DateRank', y = 'Rank', text = 'labelText',
                        level = 'glyph', source = source, text_font_size = '8pt',
                        text_align = 'center',text_baseline = 'middle', render_mode = 'canvas')
        p.add_layout(labels)
        p.select_one(HoverTool).tooltips = [
            ("Rank, DateRank", '@Rank , @DateRank'),
            ('SpG', str(spg)),
            ('Count', '@Count'),
            ('Expected', '@Expected'),
            ('Proportion', '@Prop'),
            ('AbsZScore', '@AbsZ'),
            ('pValue', '@pVal')
        ]

        return p

    plotDict = {}
    for spg in df['SpG'].unique():
        plotDF = df[df['SpG'] == spg]
        plotDict[spg] = unaggPlot(plotDF, spg, func)

    return layout([[plotDict[i] for i in range(1,7)],
            [plotDict[8],Spacer(**unaggFigDict['MidSpacer']), plotDict[7]],
            [plotDict[9],Spacer(**unaggFigDict['BotSpacer']), plotDict[10]]])


def aggDisplay(df, func, plotOpts):
    plotOpts = [(e[0], True) if e[1] == 'Both' ## Check?
                else e for e in plotOpts]
    headNode = TreeNode()
    buildTree(plotOpts, headNode)

    tables = treeTables(headNode)
    aggPlots = []
    for opts, tabs in tables:
        title = makeTitle(opts)
        aggTab = speciesRankDateAgg(tabs) # Add to ignore functionality
        aggPlots.append(returnAggPlot(aggTab, func, title))

    sqrt = len(aggPlots)**.5
    if sqrt.is_integer(): cols = sqrt
    else: cols = int(sqrt) +1

    return gridplot(aggPlots, ncols = cols)

def returnAggPlot(aggTab, func = 'Prop', title = '', start = 1, end = 10, figKW = defaultFigKW):
    # Add title functionality
    df = aggStackDF(aggTab, start, end)
    df = addLabelToDF(df)
    df['Rank'] = df['Rank'].astype(str)
    df['DateRank'] = df['DateRank'].astype(str)

    x_range = [str(n) for n in range(start, end+1)]
    y_range = list(reversed(x_range.copy()))

    colors = funcDict[func]['colors']

    low, high = calcColRange(df, func, funcDict[func]['center'])
    mapper = funcDict[func]['cmapper'](palette = colors, low = low, high = high)


    source = ColumnDataSource(df)

    p = figure(title = func, x_range = x_range, y_range = y_range, **figKW)
    p = setPlotStyle(p)

    p.rect(x = 'DateRank', y = 'Rank', width = 1, height = 1,
            source = source, dilate = True,
            fill_color = {'field': func, 'transform':mapper},
            line_color = None)
    labels = LabelSet(x = 'DateRank', y = 'Rank', text = 'labelText',
                            level = 'glyph', source = source, text_font_size = '8pt',
                            text_align = 'center',text_baseline = 'middle',
                            render_mode = 'canvas')
    p.add_layout(labels)
    p.select_one(HoverTool).tooltips = [
            ("Rank, DateRank", '@Rank , @DateRank'),
            ('Count', '@Count'),
            ('Expected', '@Expected'),
            ('Proportion', '@Prop'),
            ('AbsZScore', '@AbsZ'),
            ('pValue', '@pVal')
    ]
    return p
