from typing import Dict

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

NUTS3 = dict(
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
    return NUTS3[short]
