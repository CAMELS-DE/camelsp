from typing import Dict
import os

# This package is intended to be installed along with the data folder
BASEPATH = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_INPUT_PATH = os.path.abspath(os.path.join(BASEPATH, '..', 'input_data'))
_DEFAULT_OUTPUT_PATH = os.path.abspath(os.path.join(BASEPATH, '..', 'output_data'))
INPUT_PATH = os.environ.get('INPUT_DIR', _DEFAULT_INPUT_PATH)
OUTPUT_PATH = os.environ.get('OUTPUT_DIR', _DEFAULT_OUTPUT_PATH)


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
    'ne': 'ne',
    'niedersachsen': 'ne',
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
    ne='DE9',
    nrw='DEA',
    rlp='DEB',
    sl='DEC',
    sn='DED',
    sa='DEE',
    sh='DEF',
    th='DEG'
)


def nuts(key: str) -> str:
    short = __BL_TRANS.get(key.lower(), key.lower())
    return _NUTS[short]


def get_path(bl: str = None):
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
