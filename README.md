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

We use nuts2 codes to derive ids and to build a folder structure. There is a case-insensitve utility function
for looking up the top level 2 NUTS codes in the package, which should accept many existing abbreviations:

```python
from camelsp import nuts3

nuts('Ba-Wü')                  # gives DE1
nuts('NRW')                    # gives DEA
nuts('Pfalz')                  # gives DEB
nuts('mecklenburg Vorpommern') # gives DE8
```

## save new data

The `Bundesland` context manager accepts any kind of data, to be added to the CAMELS dataset. Within a context, the manager has the `save_timeseries` function, which takes a `pd.DataFrame` with columns `['date', <variable>, 'flag']` and merges them with possibly existing data:

```python
df = read_in_function()

with Bundesland('Bayern') as bl:
    bl.save_timeseries(df, series_id='DE210060')

```

## metadata

There are two ways how the current metdata can be read. 

This will read all metadata of all federal states into a single `DataFrame`

```python
from camelsp import get_metadata
get_metadata()
```

Or for only one federal state:

```python
from camelsp import Bundesland

with Bundesland('Sachsen') as bl:
    print(bl.metadata)
```

The context manager can also update the metadata. This can only be done on federal state level.
The new metadata needs to reference an **existing** column in the metadata and will default to
`'camels_id'` or `'provider_id'` if not given. All other columns in the new `DataFrame` 
will be updated (created or overwritten) for the respective federal state **only**.

```python
# get the new metadata from somewhere
new_metadata = read_new_metadata()


with Bundesland('Sachsen-Anhalt') as bl:
    # either use the property setter shortcut - this can only handle updates on camels or provider id
    bl.metadata = new_metadata

    # OR the function - use other column optionally
    bl.update_metadata(new_metadata, 'existing_primary_key')
```