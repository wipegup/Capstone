from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets

widgets.Dropdown(
    options={'One': 1, 'Two': 2, 'Three': 3},
    value=2,
    description='Number:',
)

widgets.Dropdown(
    options=['1', '2', '3'],
    value='2',
    description='Number:',
    disabled=False,
)

widgets.RadioButtons(
    options=['pepperoni', 'pineapple', 'anchovies'],
#     value='pineapple',
    description='Pizza topping:',
    disabled=False
)

widgets.Checkbox(
    value=False,
    description='Check me',
    disabled=False
)

widgets.BoundedIntText(
    value=7,
    min=0,
    max=10,
    step=1,
    description='Text:',
    disabled=False
)

widgets.IntSlider(
    value=7,
    min=0,
    max=10,
    step=1,
    description='Test:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)

widgets.Text(
    value='Hello World',
    placeholder='Type something',
    description='String:',
    disabled=False
)
