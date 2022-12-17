from __future__ import annotations
from typing import Union, Dict
from types import TracebackType
from contextlib import AbstractContextManager
import os
import json
import warnings

import pandas as pd

from .util import nuts, get_path, BASEPATH


class Bundesland(AbstractContextManager):
    """"""
    def __init__(self, bl: str, work_dir: str = None):
        # set the Bundesland
        self.NUTS = nuts(bl)

        # set output path
        self.output_path = get_path(bl)
    
    def __enter__(self) -> 'Bundesland':
        return super().__enter__()
    
    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        return super().__exit__(__exc_type, __exc_value, __traceback)

    @property
    def column_mapping(self) -> Dict[str, str]:
        with open(os.path.join(BASEPATH, 'column_mapping.json'), 'r') as f:
            return json.load(f)
    
    @column_mapping.setter
    def column_mapping(self, new_map: Dict[str, str]):
        # get the current mapping
        mapping = self.column_mapping

        # check if we have conflicting column names
        conflicts = [(k, v, ) for k, v in new_map.items() if k in mapping and mapping[k] != v.lower()]
        if len(conflicts) > 0:
            conf_str = [f'{k} -> {v}' for (k, v) in conflicts]
            warnings.warn(f"CONFLICTING HEADER RENAMES. The following header can't be set as they are already defined: {', '.join(conf_str)}")

        # use only lower-case values and ignore conflicts
        conficting_keys = [t[0] for t in conflicts]
        updates = {k: v.lower() for k, v in new_map.items() if k not in conficting_keys}

        # update
        mapping.update(updates)

        # save
        with open(os.path.join(BASEPATH, 'column_mapping.json'), 'w') as f:
            json.dump(mapping, f, indent=4)
        
    def save_raw_metadata(self, meta: pd.DataFrame, id_column: Union[str, int]) -> str:
        """
        Pass the raw metadata dump to save it to the output locations.
        A raw dump is stored to the processing folder and the ids 
        are added to the third-party-id <-> nuts_id lookup table.

        Parameters
        ----------
        meta : pandas.DataFrame
            Raw metadata dump. Nothing has to be renamed, but any information
            provided should be included.
        id_column : str, int
            Identifies the vendor's ID column in the dump.
            This is necessary to map these IDs to out NUTS ids.
        
        Returns
        -------
        path : str
            Output path in the file system for reference
        """
        pass

    def save_timeseries(self, timeseries: pd.DataFrame, third_party_id: str) -> str:
        """
        Pass a final formatted timeseries as pandas DataFrame, without index.
        The date column should be a data column, along with the variable and the 
        quality flag (True / False; as was checked yes / no)
        The columns will be renamed given the global rename dictionary defined
        as 'column_mapping.json'. Adding renames to the config is preferred over
        renaming in the calling script as the renames are more transparent then.

        Parameters
        ----------
        timeseries : pandas.DataFrame
            DataFrame with at least three columns: 'date', the variable (q, w)
            and 'flag'.
        third_party_id : str
            The vendor's id of this timeseries. This will be used to look up
            the correct new id and storage location.
        
        Returns
        -------
        path : str
            Output path in the file system for reference
        """
        pass