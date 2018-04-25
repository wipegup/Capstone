from math import pi
import pandas as pd

from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
)
from bokeh.palettes import brewer
from bokeh.plotting import figure

from matplotlib.colors import rgb2hex
from matplotlib.pyplot import get_cmap

cw = get_cmap('coolwarm')
cwr = get_cmap('coolwarm_r')

cw = [rgb2hex(cw(i)[:3]) for i in range(256)]
cwr = [rgb2hex(cwr(i)[:3]) for i in range(256)]

import pickle
%matplotlib inline
with open('df.pickle', 'rb') as f:
    df = pickle.load(f)
exec(open('./GroupingClasses.py').read())
tabs = returnTable(df)
agg = speciesRankDateAgg(tabs)

df = dfAgg(agg, countsApply)
df.index.name = 'Rank'
df.columns.name = 'DateRank'

DateRanks = [str(e) for e in list(df.columns)]
SequenceRanks = [str(e) for e in list(df.index)]

df = pd.DataFrame(df.stack(), columns = ['amt']).reset_index()
df['Rank'] = df['Rank'].astype(str)
df['DateRank'] = df['DateRank'].astype(str)

colors = cw
mapper = LinearColorMapper(palette = colors, low = df['amt'].min(), high = df['amt'].max())

source = ColumnDataSource(df)

TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

p = figure(title = "Counts", x_range = DateRanks, y_range = list(reversed(SequenceRanks)),
            x_axis_location = 'above', plot_width = 900, plot_height = 900,
            tools = TOOLS, toolbar_location = 'below')
p.grid.grid_line_color = 'black'
p.axis.axis_line_color = 'red'
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "5pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = pi / 3

p.rect(x = "DateRank", y = "Rank", width = .9, height = .9,
        source = source,
        fill_color = {'field':'amt', 'transform':mapper},
        line_color = None)

p.select_one(HoverTool).tooltips = [
            ('Rank', '@Rank'),
            ('DateRank', '@DateRank'),
            ('Number', '@amt')
]

show(p)
