## Bird Taxa Distributions


### Introduction
Each species of bird is in a genus.  
Within those genera, the species are ordered by the extent they are "derived."  
"Derivation" is something like the "newness" of the species.  

Thus the first listed species in a bird genus is the "oldest" and the last is the "youngest"  
The ordering of species is conventionally referred to as the "sequence," I will also refer to is as the "rank".  

Similarly, each species has a date of first description. Thus each species along with a sequence/rank also has a "date rank," which refers to the order in which the species was described *in relation to the other species in its genus*.

The primary *goal* for this project was to build a tool which to create heatmaps visualizing the distribution of taxonomic rank, date rank.  

### Bokeh Interactive
The source files for the Bokeh Interactive can be found in `./BokehInteractive/`.  

The interactive itself can be run from `Interactive.ipynb` which depends on `Interactive.py` and the `./data` directory.

All these files can be found in the `Interactive.zip`  

After running the import cell:
```
from bokeh.io import output_notebook
output_notebook()
exec(open('./Interactive.py').read())
```

You have access to the `Interact()` function which will pull up a widget dashboard  

#### Controls
##### Plot Types

There are two plot types, "Aggregated" and "Unaggregated." Switching between these occurs on the tabs at the top of the widgets.  


"Unaggreated" plots will brings up a dashboard of ten plots, one for each genera of one species per genus, two species per genus, through ten species per genus.  

"Aggregated" plots all species of the specified range of ranks (default 1-10) that are in the same date rank range.  

##### Rankings  

The `Rankings` drop down speciefies which "rankings" to use, either `Genetic` or as they appear in the IOC's Birds of the world 8.1, `Alphabetized` where rank is determined by alphabetical order of species epithet, or `Random` rankings.  

##### Plotted  

The heatmaps can be colored by:  
`Proportion` which is the total number of observed species at a rank/date rank pair over the expected number of observations at that rank/date rank pair.  
`Absolute z-score` which is the absolute z-score as calculated from those observed/expected values.  
`p-value` which is the p-value calculated form those observed/expected values (N.B. p-values do not necessarily meet the requirements for their calculations, e.g. 5 observations of each kind).  
`Count` Which is the total number of observations at the rank/date rank pair.  

##### Epochs

#### Bugs
Sometimes visualizations will persist (for aggregated heatmaps), and the import cell must be re-run to clear them.

Each time you wish to create a new visualization the `Interact()` function must be re-run.  

The widget dashboard disappears after `Replot` is hit, this has to do with the fact that `Interact()` must be called separately for each visualization.

These [slides](https://docs.google.com/presentation/d/1lGLv4CpmHUvI-FvIDLxt898AzNwjlgwsl4Zc_ZBXpa4/edit) offer a couple pre-made visualizations which might be useful
