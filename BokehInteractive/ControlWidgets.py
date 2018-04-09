import ipywidgets as widgets
from ipywidgets import (Layout, HBox, VBox, Dropdown, RadioButtons,
                        ToggleButton, Checkbox, Label, Text, Button,
                        BoundedIntText, Tab, IntRangeSlider)

import operator as op
import pickle

#####
# Widget Definitions
#####

    #####
    # Widget Spacers
    #####
def makeVSpace(px = '10px'):
    return Label(layout = Layout(height = px))
def makeHSpace(px = '25px'):
    return Label(layout = Layout(width = px))

vSpace = makeVSpace()
hSpace = makeHSpace()

    #####
    # Widget Defaults
    #####
rangeTextDefaults = {'min' : 1757, 'max': 2020,
                    'layout': Layout(width = '150px')}
    ######
    # Common Widgets
    #####
source = Dropdown( options = {'Genetic':'real',
                            'Alphabetized':'alpha',
                            'Random':'rand'},
                    description = 'Rankings', layout = Layout(width = '50%'))

func = Dropdown( options = {'Proportion':'Prop',
                            'Absolute z-score':'AbsZ',
                            'p-Value':'pVal',
                            'Count':'Count'},
                    description = 'Plotted')

replotButton = Button(description="Replot")#, layout = Layout(height = '100px'))

epochKind =  Dropdown(
                    options = {'Species':'SDate', 'Genus':'GDate'},
                    value = 'SDate', description = 'Dates',
                    layout = Layout(width = '160px'))

SpVG = Dropdown( options = [None,'>', '>=', '<', '<=', '==','!='],
                description = 'vs. oper',
                layout = Layout(width = '150px') )
svgLabel = Label('s. Description vs. G Erection Dates')

SVGgroup = VBox([svgLabel, SpVG])


topRowGroup = HBox([source, func, hSpace, replotButton])

    #####
    # UnAgg
    #####

unaggBools = {'options' :{'True':True, 'False':False, 'Both':None},
                'value' : None
                }

UAOGenus = RadioButtons( **unaggBools,
                        description = 'In Orig. Gen.')

UATspecies = RadioButtons( **unaggBools,
                        description = 'TypeSpecies')

UAEpochCheck = Checkbox( value = False, description = 'Date Range')


UAEStart = BoundedIntText( value = 1757,
                    description='Start:', **rangeTextDefaults)
UAEEnd = BoundedIntText( value = 2020,
                    description='End:', **rangeTextDefaults)

widgets.widget_link.Link((UAEStart, 'value'), (UAEEnd, 'min'))
widgets.widget_link.Link((UAEEnd, 'value'), (UAEStart, 'max'))

unaggWidg = VBox([
                topRowGroup,
                HBox([UATspecies, UAOGenus, SVGgroup,
                    VBox([
                        HBox([UAEpochCheck, epochKind]),
                        HBox([UAEStart, UAEEnd])
                    ])
                ])
            ])

    #####
    # Agg
    #####

######
### Epochs
######
defaultEpochs = {1: [1757,1815], 2:[1816,1915], 3:[1915,2020]}

epochControls = {}
epochControls['OnOff'] = ToggleButton(value = False, description = 'Epochs',
                                        layout = Layout(width = '100px'))
def checkOnOff(b):
    if type(b['new']) == bool:
        v = b['new']
        if v:
            epochControls['OnOff'].value = True

for i in range(1,4):
    epochControls[i] = {}
    work = epochControls[i]
    work['check'] = Checkbox(
            value = False, description='Epoch ' + str(i))
    work['beg'] = BoundedIntText( value = defaultEpochs[i][0],
                        description='Start:', **rangeTextDefaults)
    work['end'] = BoundedIntText( value = defaultEpochs[i][1],
                        description='End:', **rangeTextDefaults)

    widgets.widget_link.Link((work['beg'], 'value'), (work['end'], 'min'))
    widgets.widget_link.Link((work['end'], 'value'), (work['beg'], 'max'))
    work['check'].observe(checkOnOff)

    work['display'] = VBox([
                        HBox([work['check'], Label()]),
                        HBox([work['beg'],work['end']])
                        ])

def resetEpochCheckBoxes(b):
    #print(b)
    if b['name']=='value':
        newV = b['new']
        if newV:
            epochControls[1]['check'].value = True
        else:
            for i in range(1,4):
                epochControls[i]['check'].value = False

epochControls['OnOff'].observe(resetEpochCheckBoxes)

epochGroup = HBox([
                VBox([
                    HBox([epochControls['OnOff'], epochKind]),
                    epochControls[1]['display']
                    ]),
                VBox([epochControls[i]['display']for i in range(2,4)])
                ])

SVGChooser = Dropdown( options = {'Only':True, 'Not':False, 'Both':[True, False]},
                value = [True, False], layout = Layout(width = '150px'))

aggSVGgroup = VBox([SVGgroup, SVGChooser])

midLine = HBox([epochGroup, aggSVGgroup])

aggBools = {'options':{'NoSplit': None, 'True': True,
    'False': False, 'Split': [True,False]},'value':None
            }

AOGenus = RadioButtons( **aggBools,
                        description = 'In Orig. Gen.', disabled = False)

ATspecies = RadioButtons( **aggBools,
                        description = 'TypeSpecies')

######
### SPG toIgnore
######

spgSelector = {}
spgSelector['which'] = Dropdown( options = {'Only':True, 'Not':False},
                            value = False, layout = Layout(width = '150px'))

spgSelector['reset'] = Button(description = 'Reset')
for i in list(range(1,11)) + [11,21,31]:
    if i < 11:
        spgSelector[i] = Checkbox(value = False, description = str(i))
    else:
        spgSelector[i] = Checkbox(value = False, description = '>' + str(i-1))

spgSelector[1].value = True

def resetSpGCheckBoxes(b):
    for k in spgSelector:
        if type(k) == int:
            spgSelector[k].value = False
    spgSelector[1].value = True

spgSelector['reset'].on_click(resetSpGCheckBoxes)

spgSelectorLayout = HBox([
                        VBox([spgSelector[i] for i in range(1,6)]),
                        VBox([spgSelector[i] for i in range(6,11)]),
                        VBox([spgSelector[i] for i in [11,21,31,'which','reset']])
                    ])

bottLine = HBox([AOGenus, ATspecies, spgSelectorLayout])

startEnd = IntRangeSlider( value = [1,10], min = 1, max = 10, step = 1,
                description = 'Ranks')

aggWidg = VBox([topRowGroup, midLine, bottLine, startEnd])

kind = Tab()
kind.children = [aggWidg, unaggWidg]
for i, name in enumerate(['Aggregated','Unaggregated']):
    kind.set_title(i, name)
