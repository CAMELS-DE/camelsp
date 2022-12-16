# camelsp

This repo helps processing the data dumps received from the authorities. 

It is important to install the package locally and with editable flag:

```bash
git clone git@github.com:camels-de/camelsp
cd camelsp
pip install -e .

# then wget the data into the input data folder
cd input_data
wget https://bwsyncarndshare.kit.edu/s/<SHARE_TOKEN>/download
```

## Scripts

Functions for handling one state specifically are located in the respective subbmodule,
utility functions helpful for all states are imported at top-level

Help scripts indicating the usage for possible re-processing are located at the top-level
`scripts` folder.

## NUTS

We use nuts3 codes to derive ids and to build a folder structure. There is a case-insensitve utility function
for looking up the top level 3 NUTS codes in the package, which should accept many existing abbreviations:

```python
from camelsp import nuts3

nuts3('Ba-Wü')                  # gives DE1
nuts3('NRW')                    # gives DEA
nuts3('Pfalz')                  # gives DEB
nuts3('mecklenburg Vorpommern') # gives DE8
```