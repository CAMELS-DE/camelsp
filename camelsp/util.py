import os
import json 
import pandas as pd
import numpy as np

# This package is intended to be installed along with the data folder
BASEPATH = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_INPUT_PATH = os.path.abspath(os.path.join(BASEPATH, '..', 'input_data'))
_DEFAULT_OUTPUT_PATH = os.path.abspath(os.path.join(BASEPATH, '..', 'output_data'))
INPUT_PATH = os.environ.get('INPUT_DIR', _DEFAULT_INPUT_PATH)
OUTPUT_PATH = os.environ.get('OUTPUT_DIR', _DEFAULT_OUTPUT_PATH)


def _get_logo():
    with open(os.path.join(BASEPATH, 'logo.bin'), 'r') as f:
        return f"data:image/png;base64,{f.read()}"


# helper 
__BL_TRANS = {
    'bw': 'bw',
    'baden-wuerttemberg': 'bw',
    'baden-württemberg': 'bw',
    'ba-wü': 'bw',
    'bayern': 'by',
    'by': 'by',
    'berlin': 'b',
    'b': 'b',
    'ber': 'b',
    'br': 'br',
    'brandenburg': 'br',
    'hb': 'hb',
    'bremen': 'hb',
    'hh': 'hh',
    'hamburg': 'hh',
    'hessen': 'he',
    'he': 'he',
    'mecklenburg-vorpommern': 'mp',
    'mp': 'mp',
    'meckpom': 'mp',
    'meck-pom': 'mp',
    'mecklenburg vorpommern': 'mp',
    'nis': 'nis',
    'niedersachsen': 'nis',
    'nrw': 'nrw',
    'nordrhein-westfalen': 'nrw',
    'nordrhein westfalen': 'nrw',
    'rlp': 'rlp',
    'rheinland-pfalz': 'rlp',
    'rheinland pfalz': 'rlp',
    'pfalz': 'rlp',
    'sl': 'sl',
    'saarland': 'sl',
    'sn': 'sn',
    'sachsen': 'sn',
    'sa': 'sa',
    'sachsen-anhalt': 'sa',
    'sachsen anhalt': 'sa',
    'sh': 'sh',
    'schleswig-holstein': 'sh',
    'schleswig holstein': 'sh',
    'th': 'th',
    'thüringen': 'th',
    'thueringen': 'th'
}

_NUTS = dict(
    bw='DE1',
    by='DE2',
    b='DE3',
    br='DE4',
    hb='DE5',
    hh='DE6',
    he='DE7',
    mp='DE8',
    nis='DE9',
    nrw='DEA',
    rlp='DEB',
    sl='DEC',
    sn='DED',
    sa='DEE',
    sh='DEF',
    th='DEG'
)

_INPUT_DEFAULT_PATHS = dict(
    DE1='BW_Baden_Wuerttemberg',
    DE2='BY_Bayern/Abfluss_Pegel/Datenanfrage_CAMELS-DE',
    DE3='B_Berlin',
    DE4='BR_Brandenburg',
    DE5='HB_Bremen',
    DE6='HH_Hamburg',
    DE7='HE_Hessen',
    DE8='MP_Mecklenburg_Vorpommern',
    DE9='NiS_Niedersachsen',
    DEA='NRW_Nordrhein-Westfalen',
    DEB='RLP_Rheinland-Pfalz',
    DEC='SL_Saarland',
    DED='SN_Sachsen',
    DEE='SA_Sachsen-Anhalt',
    DEF='SH_Schleswig-Holstein',
    DEG='TH_Thueringen'
)


_NUTS_LVL2_NAMES = dict(
    DE1='Baden-Württemberg',
    DE2='Bayern',
    DE3='Berlin',
    DE4='Brandenburg',
    DE5='Bremen',
    DE6='Hamburg',
    DE7='Hessen',
    DE8='Mecklenburg Vorpommern',
    DE9='Niedersachsen',
    DEA='Nordrhein-Westfalen',
    DEB='Rheinland-Pfalz',
    DEC='Saarland',
    DED='Sachsen',
    DEE='Sachsen-Anhalt',
    DEF='Schleswig-Holstein',
    DEG='Thüringen'
)

def nuts(key: str) -> str:
    short = __BL_TRANS.get(key.lower(), key.lower())
    if short in _NUTS.keys():
        return _NUTS[short]
    elif short.upper() in _NUTS.values():
        return short.upper()
    else:
        raise IndexError(f"No idea what {key} should translate to")


def get_output_path(bl: str = None):
    """
    Return the base output path for the given BundesLand (bl).
    If no bl is given, return the output root folder
    """
    # get the output path
    if bl is None:
        return OUTPUT_PATH
    
    # get the bundesland
    bl_folder = nuts(bl)
    return os.path.join(OUTPUT_PATH, bl_folder)


def get_input_path(bl: str = None):
    """
    Return the base input path for the given Bundesland (bl).
    If no bl is given, return the input root folder.
    """
    # check if bl is given
    if bl is None:
        return INPUT_PATH
    
    # get the bundesland
    if bl in _INPUT_DEFAULT_PATHS.keys():
        bl_folder = _INPUT_DEFAULT_PATHS[bl]
    else:
        bl_folder = _INPUT_DEFAULT_PATHS[nuts(bl)]

    # return the path
    return os.path.join(INPUT_PATH, "Q_and_W", bl_folder)


def get_full_nuts_mapping(base_path = OUTPUT_PATH, format='json'):
    """Get the NUTS mapping to provider_id for ALL states"""
    # build file name
    fname = os.path.join(base_path, 'metadata', 'nuts_mapping.json')

    # if nuts_mapping does not exist, create empty mapping
    if not os.path.exists(fname):
        js = [{}]
        print(f"Can't find the nuts_mapping at {fname}, returning empty mapping.")
    # nuts_mapping exists: read
    else:
        with open(fname, 'r') as f:
            js = json.load(f)
    
    # return
    if format.lower() == 'json':
        return js
    elif format.lower() in ('csv', 'df', 'dataframe'):
        return pd.DataFrame(js)


def get_metadata(base_path = OUTPUT_PATH) -> pd.DataFrame:
    """Get the current state of overall metadata"""
    # get the path
    path = os.path.join(base_path, 'metadata', 'metadata.csv')

    if os.path.exists(path):
        return pd.read_csv(path, dtype={'provider_id': str})
    else:
        # generate
        mapping =  get_full_nuts_mapping(base_path=base_path, format='df')
        
        # rename header
        mapping.columns = ['camels_id', 'provider_id', 'camels_path']

        # bugfix for early stages of the mapping
        #mapping['provider_id'] = mapping.provider_id.astype(str)

        # some extra columns for convenience
        mapping['nuts_lvl2'] = [nid[:3] for nid in mapping.camels_id]
        mapping['federal_state'] = [_NUTS_LVL2_NAMES[nid[:3]] for nid in mapping.camels_id]

        return mapping


def update_metadata(new_metadata: pd.DataFrame, base_path = OUTPUT_PATH, id_column: str = None):
    """
    Update the the full metadata table using a update dataframe.
    The new dataframe as to include either the camels_id or the provider_id and that
    will be used for updateing. The new_metadata DataFrame may be smaller as the full 
    table. Existing columns will be updated, missing columns will be added and filled with
    NA for all IDs that are not present in new_metadata.
    If index_col is not provided
    """
    # get metadata
    metadata = get_metadata(base_path=base_path)
    
    if new_metadata.index.name in ['provider_id', 'camels_id', id_column if id_column is not None else 'FOOBAR']:
        new_metadata.reset_index(inplace=True)

    # check id column
    if id_column is None:
        if 'camels_id' in new_metadata.columns:
            id_column = 'camels_id'
        elif 'provider_id' in new_metadata.columns:
            id_column = 'provider_id'
    
    # check id_column
    if id_column is None:
        raise AttributeError("You need to specify the id_column, or 'camels_id' or 'provider_id' has to be present.")
    
    # update none existing columns
    for col in new_metadata.columns:
        if col not in metadata.columns:
            metadata[col] = np.NaN
    
    # try to set the id_column as index
    metadata.set_index(id_column, inplace=True)

    # update
    metadata.update(new_metadata.set_index(id_column))
    metadata.reset_index(inplace=True)

    # overwrite
    path = os.path.join(base_path, 'metadata', 'metadata.csv')
    metadata.to_csv(path, index=False)
