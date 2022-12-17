from __future__ import annotations
from typing import Union, Dict, List
from types import TracebackType
from contextlib import AbstractContextManager
import os
import json
import warnings
import shutil

import pandas as pd

from .util import nuts, get_path, BASEPATH, INPUT_PATH


class Bundesland(AbstractContextManager):
    """"""
    def __init__(self, bl: str, work_dir: str = None):
        # set the Bundesland
        self.NUTS = nuts(bl)

        # set output path
        self.output_path = get_path(bl)
        self.meta_path = os.path.abspath(os.path.join(get_path(), 'metadata'))
    
        # for easier access store the default input path as well
        self.input_path = INPUT_PATH

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

    @property
    def nuts_mapping(self) -> List[Dict[str, str]]:
        # check if the final metadata directly exists
        if not os.path.exists(self.meta_path):
            os.makedirs(self.meta_path)
        map_path = os.path.join(self.meta_path, 'nuts_mapping.json')
        
        # create the mapping
        if os.path.exists(map_path):
            with open(map_path, 'r') as f:
                mapping = json.load(f)
        else:
            mapping = []
        
        return mapping
    
    @property
    def nuts_table(self) -> pd.DataFrame:
        return pd.DataFrame(self.nuts_mapping)

    @nuts_mapping.setter
    def nuts_mapping(self, new_nuts: List[Dict[str, str]]):
        # get the current nuts mapping
        mapping = self.nuts_mapping

        # TODO: generate warnings if we have the nuts or the provider ids

        # extend the mapping
        mapping.extend(new_nuts)
        
        # save
        with open(os.path.join(self.meta_path, 'nuts_mapping.json'), 'w') as f:
            json.dump(mapping, f, indent=4)

        # generate a csv for Michi Stoelzle ;)
        df = pd.DataFrame(mapping)
        df.to_csv(os.path.join(self.meta_path, 'nuts_mapping.csv'), index=False)
        
    def save_raw_metadata(self, meta: pd.DataFrame, id_column: Union[str, int], overwrite: bool = False) -> str:
        """
        Pass the raw metadata dump to save it to the output locations.
        A raw dump is stored to the processing folder and the ids 
        are added to the third-party-id <-> nuts_id lookup table.

        This function will overwrite existing raw metadata and possibly
        empty existing data output directories, if overwrite is set to
        True.

        Parameters
        ----------
        meta : pandas.DataFrame
            Raw metadata dump. Nothing has to be renamed, but any information
            provided should be included.
        id_column : str, int
            Identifies the vendor's ID column in the dump.
            This is necessary to map these IDs to out NUTS ids.
        overwrite : bool
            If True, any existing data output directory will be removed.
            This can be helpful, when the metadata changed and consequently
            the original provider_id have another associated nuts_id.
        
        Returns
        -------
        path : str
            Output path in the file system for reference
        """
        # check if the raw metadata directory exists
        path = os.path.abspath(os.path.join(self.output_path, '..',  'raw_metadata'))
        if not os.path.exists(path):
            os.makedirs(path)
        
        # extract the meta-ids
        if isinstance(id_column, int):
            meta_ids = meta.iloc[:, id_column].values
        else:
            meta_ids = meta.loc[:, id_column].values
        
        # force provider ids to be strings
        meta_ids = [str(_) for _ in meta_ids]
        
        # generate a mapping from original to NUTS 
        nuts_mapping = list()
        for i, meta_id in enumerate(meta_ids):
            # generate nuts id
            nuts_id = f"{self.NUTS}{'%.5d' % (10000 + i * 10)}"
            out_dir = os.path.join(self.output_path, nuts_id)

            # add the mapping
            nuts_mapping.append({
                'nuts_id': nuts_id,
                'provider_id': meta_id, 
                'path': os.path.relpath(os.path.join(out_dir, 'data.csv'), start=os.path.join(self.output_path, '..'))
            })

            # warn if the folder already exists
            if os.path.exists(out_dir):
                if overwrite:
                    shutil.rmtree(out_dir)
                else:
                    warnings.warn(f"Generated NUTS id {nuts_id} for {meta_id}, which already exists."
                         "Make sure that the mapping is still correct or use the overwirte=True flag to overwrite the data")

            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
        
        # store raw metadata
        meta.to_csv(os.path.join(path, f'{self.NUTS}_raw_metadata.csv'), index=False)

        # update the mapping
        self.nuts_mapping = nuts_mapping

        return path

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