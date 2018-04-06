from IPython.display import display, clear_output

import ipywidgets as widgets
from ipywidgets import (Layout, HBox, VBox, Dropdown,RadioButtons,
                        ToggleButton, Checkbox, Label, Text, Button,
                        BoundedIntText)

OGenus = RadioButtons( options = [None, True, False,'Both'], description = 'In Orig. Gen.')

def clicked(b):
    #print(b)
    if b['name']=='value':
        newV = b['new']
        if newV:
            epochControls[1]['check'].value = True
        else:
            for i in range(1,4):
                epochControls[i]['check'].value = False

epochControls = {}
epochControls['OnOff'] = ToggleButton(value = False, description = 'Epochs', layout = Layout(width = '100px'))
epochControls['OnOff'].observe(clicked)
epochControls['Kind'] = Dropdown( options = {'Species':'s', 'Genus':'g'},
                            value = 's', description = 'Epoch Type',
                            layout = Layout(width = '160px'))
for i in range(1,4):
    epochControls[i] = {}
    work = epochControls[i]
    work['check'] = Checkbox(
            value=False, description='Epoch ' + str(i))
    work['beg'] = BoundedIntText(
        value = 1757, min = 1757, max = 2020,
        description='Start:', layout = Layout(width = '150px'))
    work['end'] = BoundedIntText(
        value = 2020,min =1757, max = 2020,
        description='End:', layout = Layout(width = '150px'))
    widgets.widget_link.Link((work['beg'],'value'),(work['end'], 'min'))
    widgets.widget_link.Link((work['end'],'value'),(work['beg'],'max'))


    #widgets.
    work['display'] = VBox([HBox([work['check'], Label()]),HBox([work['beg'],work['end']])])

epochGroup = HBox([
                VBox([HBox([epochControls['OnOff'], epochControls['Kind']]),
                epochControls[1]['display']]),
                VBox([epochControls[i]['display']for i in range(2,4)])
                , OGenus])

def makeVspace(px = '10px'):
    return Label(layout = Layout(height = px))
def makeHspace(px = '25px'):
    return Label(layout = Layout(width = px))
vspace = makeVspace()
hSpace = makeHspace()
source = Dropdown(options = {'Real':'real','Alphabetized':'alpha','Random':'rand'},
                description = 'Rankings')
kind = Dropdown( options = {'Aggregated':True, 'Unaggregated':False}, description = 'Plot Type')
func = Dropdown( options = {'Proportion':'Prop', 'Absolute z-score':'AbsZ', 'p-Value':'pVal', 'Count':'Count'}, description = 'Plotted')
Tspecies = RadioButtons( options = [None,True, False, 'Both'], description = 'TypeSpecies')
replotButton = Button(description="Replot", layout = Layout(height = '100px'))

replotButton.on_click(replot)
SpVG = Dropdown( options = [None, '>','>=','<','<=','==','!='], description = 'vs. oper',
              layout = Layout(width = '150px'))
svgLabel = Label('s. Description vs. G Erection Dates')
SVGgroup = VBox([svgLabel, SpVG])
endGroup = HBox([SVGgroup, hSpace, Tspecies, makeHspace('200px'), replotButton])
sourceGroup = HBox([ source, kind, func])
allWidgs = VBox([sourceGroup,vspace,epochGroup,vspace, endGroup])
