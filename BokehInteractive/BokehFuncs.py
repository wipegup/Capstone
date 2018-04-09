from bokeh.models import (
    ColumnDataSource, HoverTool, LinearColorMapper,
    BasicTicker, PrintfTickFormatter, ColorBar, LogColorMapper,
    LabelSet, Spacer )
from bokeh.plotting import figure
from bokeh.layouts import gridplot, layout

from matplotlib.colors import rgb2hex
from matplotlib.pyplot import get_cmap

#####
# Color Retreival
#####

cw = get_cmap('coolwarm')
cwr = get_cmap('coolwarm_r')

cw = [rgb2hex(cw(i)[:3]) for i in range(256)]
cwr = [rgb2hex(cwr(i)[:3]) for i in range(256)]

#pVallinearColorMaps =
#x = [1, 64, 128, 192, 256] $$$$
#y = [0,.01, .05, .1, .5]


#####
# Dictionary Definitions
# Plot Styling Functions
#####
funcDict = { 'Prop':{
                'center':1,
                'cmap' : 'coolwarm',
                'colors': cw,
                'cmapper': LinearColorMapper,
                'fullName': 'Proportion'},
           'AbsZ':{
               'center': 1.64,
               'cmap': 'coolwarm',
               'colors': cw,
               'cmapper': LinearColorMapper,
               'fullName': 'Absolute z-Score'},
           'pVal':{
               'center': .10,
               'cmap': 'coolwarm_r',
               'colors': cwr,
               'cmapper':LogColorMapper,
               'fullName': 'p-Value'},
            'Count':{
                'center': 0,
                'cmap': 'coolwarm',
                'colors': cw,
                'cmapper': LinearColorMapper,
                'fullName': 'Raw Count'}
           }

######DEPRECATED?
defaultFigKW = {'plot_width': 400, 'plot_height':400,
                'tools': "hover",'x_axis_location' : 'above',
                'toolbar_location' : None}

defaultToolTips = [
            ("Rank, DateRank", '@Rank , @DateRank'),
            ('Count', '@Count'),
            ('Expected', '@Expected'),
            ('Proportion', '@Prop'),
            ('AbsZScore', '@AbsZ'),
            ('pValue', '@pVal')
    ]

def buildUnaggFigDict(x):
    toRet = {}
    for i in range(1,11):
        toRet[i] = {'plot_width': i*x, 'plot_height': i*x,
                    'tools': 'hover', 'x_axis_location': 'above',
                    'toolbar_location': None}

    toRet['MidSpacer'] = Spacer(**{'width':6*x, 'height':6*x})
    toRet['BotSpacer'] = Spacer(**{'width':2*x, 'height':2*x})
    return toRet

#####
# Auxillary
#####

def addLabelToDF(df, func):
    df['labelText'] = [round(e,1) for e in df.loc[:,func]] # Turn to string? $$$$
    return df

def calcColorRange(df, func, center):
    realMin, realMax = df[func].min(), df[func].max()
    maxSpread = np.max([center - realMin, realMax -center])
    return {'low':center-maxSpread , 'high':center + maxSpread}

def defaultPlot(p, source, func, colorRange, toolTips):

    def addRects(p, source, func, colorRange):
        mapper = funcDict[func]['cmapper'](
            palette = funcDict[func]['colors'],
            **colorRange)

        p.rect(x = 'DateRank', y = 'Rank',
            width = 1, height = 1,
            source = source, dilate = True,
            fill_color = {'field': func, 'transform': mapper},
            line_color = None)
        return p

    def addLabelsToPlot(p, source, text_font_size = '8pt'):

        labels = LabelSet(x = 'DateRank', y = 'Rank', text = 'labelText',
                        level = 'glyph', source = source,
                        text_font_size = text_font_size,
                        text_align = 'center',text_baseline = 'middle',
                        render_mode = 'canvas')
        p.add_layout(labels)

        return p

    def setPlotStyle(p):
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = '10pt'
        p.axis.major_label_standoff = 0

        return p

    p = setPlotStyle(p)
    p = addRects(p, source, func, colorRange)
    p = addLabelsToPlot(p, source)

    p.select_one(HoverTool).tooltips = toolTips

    return p

#####
# Display Functions
#####

def unaggDisplay(df, func, plotOpts = [], figscale = 45):

    def unaggPlot(df, func, colorRange, unaggFigDict):

        spg = df['SpG'].max()

        x_range = [str(n) for n in range(1, spg + 1)]
        y_range = list( reversed( x_range.copy() ) )

        source = ColumnDataSource(df)

        p = figure(title = '',
            x_range = x_range, y_range = y_range,
            **unaggFigDict[spg])

        ttWithSPG = defaultToolTips.copy()
        ttWithSPG.insert(1, ('SpG', str(spg)))

        return defaultPlot(p, source, func, colorRange, ttWithSPG)

    df = unaggStackDF(returnTable(df, plotOpts))
    df = addLabelToDF(df, func)

    title = returnTitle(plotOpts)
    colorRange = calcColorRange(df, func, funcDict[func]['center'])
    unaggFigDict = buildUnaggFigDict(figscale)

    plotDict = {}

    for spg in df['SpG'].unique():
        plotDF = df[df['SpG'] == spg]

        plotDict[spg] = unaggPlot(plotDF, func, colorRange, unaggFigDict)

    toRet = layout([
                [plotDict[i] for i in range(1,7)],
                [plotDict[8], unaggFigDict['MidSpacer'], plotDict[7]],
                [plotDict[9], unaggFigDict['BotSpacer'], plotDict[10]]
                ])

    return toRet

def aggDisplay(df, func, plotOpts = [], start = 1, end = 10, toIgnore = [1]):

    def returnAggTables(df, plotOpts):
        headNode = TreeNode(df)
        buildTree(plotOpts, headNode)

        return leafTraverse(headNode, grabTables)

    def aggPlot(df, func, colorRange, title, start, end, figKW = defaultFigKW):
        x_range = [str(n) for n in range(start, end+1)]
        y_range = list( reversed( x_range.copy() ) )

        source = ColumnDataSource(df)

        p = figure(title = title, x_range = x_range, y_range = y_range, **figKW)

        return defaultPlot(p, source, func, colorRange, defaultToolTips)

    tables = returnAggTables(df, plotOpts)
    aggPlots = []
    for opts, tabs in tables:
        title = returnTitle(opts)
        plotDF = aggStackDF(speciesRankDateAgg(tabs, toIgnore), start, end)

        aggPlots.append((title, plotDF))

    colorRange = calcColorRange(
        pd.concat([e[1] for e in aggPlots], axis = 'rows'),
        func, funcDict[func]['center'])

    aggPlots = [aggPlot(addLabelToDF(e[1], func),
                    func, colorRange, e[0], start, end)
                for e in aggPlots]

    cols = len(aggPlots) ** .5
    if cols.is_integer(): cols = int(cols)
    else: cols = int(cols) + 1

    '''
    toRet = []
    fullRows = int(len(aggPlots)/cols)
    for i in range(0, fullRows):
        toRet.append(aggPlots[i*cols: (i*cols)+cols])
    if fullRows * cols != len(aggPlots):
        toRet.append(aggPlots[fullRows * cols :])
    '''

    #print('infu')
    #print(type(gridplot(aggPlots, ncols = cols)))
    return gridplot(aggPlots, ncols = cols)
