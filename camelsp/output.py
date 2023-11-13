from __future__ import annotations
from typing import Union, Dict, List
from types import TracebackType
from contextlib import AbstractContextManager
import os
import json
import warnings
import shutil
import glob
import io
import hashlib

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pandas_profiling import ProfileReport
import geopandas as gpd

from .util import nuts, get_output_path, BASEPATH, get_input_path, get_full_nuts_mapping, _get_logo, _NUTS_LVL2_NAMES, get_metadata, update_metadata


class Bundesland(AbstractContextManager):
    """"""
    def __init__(self, bl: str):
        # set the Bundesland
        self.NUTS = nuts(bl)
        self.name = _NUTS_LVL2_NAMES[self.NUTS]

        # set output path
        self.base_path = get_output_path()
        self.output_path = get_output_path(bl)
        self.meta_path = os.path.abspath(os.path.join(get_output_path(), 'metadata'))
    
        # for easier access store the default input path as well
        self.input_path = get_input_path(bl)

        # create a template for data file names, which can be overwritten
        # TODO maybe a flag if each variable goes into its own file?
        self.fname_template = '{nuts_id}_data.csv'

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
        
        # filter out the nuts of other BL
        mapping = [m for m in mapping if m['nuts_id'].startswith(self.NUTS)]
        return mapping
    
    @property
    def nuts_table(self) -> pd.DataFrame:
        return pd.DataFrame(self.nuts_mapping)

    @nuts_mapping.setter
    def nuts_mapping(self, new_nuts: List[Dict[str, str]]):
        # generate a list of nuts_ids we want to create / update
        nuts_ids = [c['nuts_id'] for c in new_nuts]
        
        # here we need to load all nuts
        all_nuts = get_full_nuts_mapping(self.base_path, format='json')

        # if nuts mapping is empty, we can just save
        if (len(all_nuts) == 1) and (len(all_nuts[0]) == 0):
            mapping = new_nuts
        # if nuts_mapping already exists, we need to filter the new nuts
        else:
            # get the current nuts mapping, but filter the new_nuts
            mapping = new_nuts + [c for c in all_nuts if c['nuts_id'] not in nuts_ids]
        
        # save, create the directory and file if it does not exist
        if not os.path.exists(self.meta_path):
            os.makedirs(self.meta_path)
        with open(os.path.join(self.meta_path, 'nuts_mapping.json'), 'w') as f:
            json.dump(mapping, f, indent=4)

        # generate a csv for Michi Stoelzle ;)
        df = pd.DataFrame(mapping)
        df.to_csv(os.path.join(self.meta_path, 'nuts_mapping.csv'), index=False)

    @property
    def metadata(self) -> pd.DataFrame:
        # get all metadata
        meta = get_metadata(self.base_path)
        
        # filter for this BL
        return meta.where(meta.nuts_lvl2 == self.NUTS).dropna(axis=0, how='all')
    
    @metadata.setter
    def metadata(self, new_metadata: pd.DataFrame):
        if 'provider_id' in new_metadata.columns and not 'camels_id' in new_metadata.columns:
            self.update_metadata(new_metadata=new_metadata, id_column='provider_id')
        else:
            self.update_metadata(new_metadata=new_metadata)
    
    def update_metadata(self, new_metadata: pd.DataFrame, id_column: str = 'camels_id'):
        update_metadata(new_metadata, id_column=id_column)

    def save_warnings(self, warns: List[warnings.WarningMessage], posfix: str = '') -> str:
        """
        Create a error log in the metadata directory for the current BL.
        """
        # get the path
        path = os.path.join(self.meta_path, f"{self.NUTS}_error{posfix}.log")

        # write a log - overwrite if it already exists
        with open(path, 'w') as f:
            # use only the message, it has ;-separated format
            f.write("provider_id;warning_type;message;additional_context")
            f.write('\n'.join([w.message.args[0] for w in warns]))
        
        return path         

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

            # create the filename
            fname = self.fname_template.format(nuts_id=nuts_id, nuts=self.NUTS)
            # add the mapping
            nuts_mapping.append({
                'nuts_id': nuts_id,
                'provider_id': meta_id, 
                'path': './' + os.path.relpath(os.path.join(out_dir, fname), start=os.path.join(self.output_path, '..'))
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

    def save_timeseries(self, timeseries: pd.DataFrame, series_id: str = None, provider_id: str = None) -> str:
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
        provider_id : str
            deprecated. use Series id now
        series_id : str
            The id of the timeseries. This can either be the providers id or 
            the camels id.
        
        Returns
        -------
        path : str
            Output path in the file system for reference
        
        """
        # handle provider ids - these are deprecated and will be removed
        if provider_id is None and series_id is None:
            raise AttributeError("You need to specify the series_id")
        elif series_id is None and provider_id is not None:
            series_id = provider_id

        # get the nuts mapping
        nuts = self.nuts_table

        # get the path for the file
        if series_id in nuts.provider_id.values:
            fpath = nuts.where(nuts.provider_id == series_id).dropna().iloc[0, -1]
        elif series_id in nuts.nuts_id.values:
            fpath = nuts.where(nuts.nuts_id == series_id).dropna().iloc[0, -1]
        
        # generate the save path
        spath = os.path.abspath(os.path.join(self.base_path, fpath))

        # check if there is already data
        if os.path.exists(spath):
            data = pd.read_csv(spath, parse_dates=[0])
        else:
            data = pd.DataFrame(columns=['date'])
        
        # make some column magic
        col_maps = self.column_mapping
        timeseries.rename(col_maps, axis=1, inplace=True)

        # TODO: handle a flag table here?
        
        # get the column that holds the variable
        var_col = [c for c in timeseries.columns if c not in ('date', 'flag', )][0]

        # TODO if we are creating one file per variable, we can skip this part
        if 'flag' in timeseries.columns:
            flag_col = f'{var_col}_flag'
            timeseries.rename({'flag': flag_col}, axis=1, inplace=True)
        
        # merge with data
        # If preprocessing is started multiple times this will result in duplicate columns with _x/_y suffixes 
        merged = pd.merge(data.set_index('date'), timeseries.set_index('date'), how='outer', left_index=True, right_index=True).reset_index()
        
        # save
        merged.to_csv(spath, index=False, na_rep='NaN')
        
        return spath

    def get_data(self, nuts_id: str, date_index: bool = True) -> pd.DataFrame:
        """
        Read the data from the output folder and return as pandas dataframe.
        Pass the CAMELS-de nuts_id. If date_index is False, 'date' will be a
        data column and a generic range-index is used.
        """
        # get the mapping
        mapping = self.nuts_table

        # check if nuts_id is actually a nuts_id or a provider_id
        if nuts_id in mapping.provider_id.values:
            provider_id = nuts_id
            nuts_id = mapping.set_index('provider_id').loc[provider_id, 'nuts_id']
            warnings.warn(f"{nuts_id} is a provider_id and not a CAMELS-de NUTSID. provider_id might have duplicates, using the first one: {nuts_id}")
        
        # build the path
        path = os.path.join(self.output_path, nuts_id, f'{nuts_id}_data.csv')

        # read in
        df = pd.read_csv(path, parse_dates=['date'], dtype={'q': float, 'q_flag': 'boolean', 'w': float, 'w_flag': 'boolean'})

        if date_index:
            df.set_index('date', inplace=True)
        
        return df
    
    #TODO shouldn't if_exist default to raise, omit or skip? Also missing in docstring
    def generate_reports(self, nuts_ids: Union[List[str], str] = 'all', fmt: str = 'html', output_folder: str = None, if_exists: str = 'replace') -> Union[str, ProfileReport]:
        """
        Generate a JSON or HTML report of the data of the given nuts_ids.

        Parameter
        ---------
        nuts_ids : list, str
            Either a string (CAMELS-DE ID) or a list of strings. Additionally,
            the the string literal 'all' is accepted, to look up all IDs.
        fmt : str
            Return format. Can be 'html', 'json', 'object'. If Object, a 
            pandas_profiling.ProfileReport is returned. In any other case the
            respective file is written into the output folder
        output_folder : str, optional
            Alternative output location. The default location is the 
            'report' folder in the base output location.
        """
        # get all nuts ids
        if nuts_ids == 'all':
            nuts_ids = self.nuts_table.nuts_id.values.tolist()
        
        # if only one nuts_id, make it iterable
        if isinstance(nuts_ids, str):
            nuts_ids = [nuts_ids]
        
        # reports container
        reports = []

        # load the logo
        logo = _get_logo()

        # check format to interrupt before report is generated
        if fmt.lower() != 'object':
            # build the path
            if output_folder is None:
                output_folder = os.path.join(self.base_path, 'reports')
            
            # check if the output location exists
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

        # instantiate all reports
        for nuts_id in nuts_ids:
            # before reading data raise or skip if we need a report and already have it
            if fmt.lower() != 'object':
                filename = os.path.join(output_folder, f"{nuts_id}.{fmt.lower()}")
                # check if the file already exists
                if os.path.exists(filename):
                    if if_exists == 'raise':
                        raise FileExistsError(f"{filename} already exists and if_exists policy is 'raise'")
                    elif if_exists == 'omit' or if_exists == 'skip':
                        continue
            
            # load the data
            try:
                df = self.get_data(nuts_id, date_index=False)
            except FileNotFoundError:
                warnings.warn(f"ID: {nuts_id} has no data")
                continue

            # instantiate the report
            #report = ProfileReport(df=df, title=nuts_id)
            report = df.profile_report(html={'style': {'logo': logo, 'theme': 'flatly'}}, progress_bar=False, title=nuts_id, 
                                       correlations={"pearson": {"calculate": True},
                                                     "spearman": {"calculate": True}})
            
            # if return, then append to container
            if fmt.lower() == 'object':
                reports.append(report)
            
            #else write a file
            else:
                report.to_file(filename)

        # check the format type
        if fmt.lower() == 'object':
            return reports

    def generate_scatter_plots(self, nuts_ids: Union[List[str], str] = 'all', fmt: str = 'png', output_folder: str = None, if_exists: str = 'replace') -> Union[None, List[plt.Figure]]:
        """
        Generates scatterplots of the data of the given nuts_ids.

        Parameter
        ---------
        nuts_ids : list, str
            Either a string (CAMELS-DE ID) or a list of strings. Additionally,
            the the string literal 'all' is accepted, to look up all IDs.
        fmt : str
            Return format. Can be 'png', 'svg', 'pdf' or 'object'. If object, a 
            (list of) matplotlib.figure.Figure is returned. In any other case the
            respective file is written into the output folder
        output_folder : str, optional
            Alternative output location. The default location is the 
            'report' folder in the base output location.
        """
        # get all nuts ids
        if nuts_ids == 'all':
            nuts_ids = self.nuts_table.nuts_id.values.tolist()

        # if only one nuts_id, make it iterable
        if isinstance(nuts_ids, str):
            nuts_ids = [nuts_ids]

        # reports container
        scatter_plots = {}
        if fmt.lower() in ['pdf','svg']:
            warnings.warn(f"Using {fmt} format leads to large files, since every single point is included in the file. Consider using png.")

        # check format to interrupt before report is generated
        if fmt.lower() != 'object':
            # build the path
            if output_folder is None:
                output_folder = os.path.join(self.base_path, 'scatter_plots')
            # check if the output location exists
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

        # instantiate all plots
        n = len(nuts_ids)
        for i,nuts_id in enumerate(nuts_ids): # TODO maybe refactor to use tqdm in outer loop instead?
            print(f"{i:<4}/{n}",end='\r')
            # before reading data raise or skip if we already have the plot
            if fmt.lower() != 'object':
                filename = os.path.join(output_folder, f"{nuts_id}.{fmt.lower()}")
                # check if the file already exists
                if os.path.exists(filename):
                    if if_exists == 'raise':
                        raise FileExistsError(f"{filename} already exists and if_exists policy is 'raise'")
                    elif if_exists == 'omit' or if_exists == 'skip':
                        continue

            # load the data
            try:
                df = self.get_data(nuts_id)
                    
            except FileNotFoundError:
                warnings.warn(f"ID: {nuts_id} has no data")
                continue

            # Replace -999 with NaN, -999 is sometimes used to indicate invalid values
            df_nan = df.replace(-999, np.NaN)
            
            # Can't make a scatterplot, if we never have both q and w values
            overlap = ((~df_nan['q'].isna()) & (~df_nan['w'].isna())).sum()
            
            if overlap == 0:
                warnings.warn(f"{nuts_id} - Q and W were never measured at the same time.")
            else:
                
                #Generate the plot
                fig, ax = plt.subplots()
                scatter = ax.scatter(df_nan['q'], df_nan['w'], c=df_nan.index.year)
                legend1 = ax.legend(*scatter.legend_elements(),loc="lower right", title="Year")
                ax.add_artist(legend1)
                ax.set_title(nuts_id)
                ax.grid(True)
                ax.set_xlabel('q')
                ax.set_ylabel('w')
                fig.tight_layout()

                # if return, then append to list
                if fmt.lower() == 'object':
                    scatter_plots[nuts_id] = fig

                #else write a file
                else:
                    plt.savefig(filename, dpi='figure') #TODO metadata with ID, Gaugename etc. Needs a way to access more metadata
                    # clear memory after saving
                    fig.clear()
                    plt.close(fig)

        # check the format type
        if fmt.lower() == 'object':
            return scatter_plots
        return None
        

    @property
    def input_hash(self):
        """
        Calculate the SHA256 hash sum of all input files within the Bundesland's input path.

        The hash sum is calculated based on the hash sums of the individual input files.
        This property provides a convenient way to check if the input data has changed.

        Returns:
        ---------
        hsum: str
            The SHA256 hash sum of all input files within the Bundesland's input path.
        
        """
        # get filenames in input_path directory
        fnames = glob.glob(f"{self.input_path}/*")

        # sort filenames alphabetically
        fnames = sorted(fnames)

        # get hash sum dictionary for files in input_path 
        out = self.gethash(fnames)

        # calculate hash sum of hash sum dictionary
        hsum = hashlib.sha256(str(out).encode()).hexdigest()

        return hsum
    

    @property
    def output_hash(self):
        """
        Calculate the SHA256 hash sum of all input files within the Bundesland's input path.

        The hash sum is calculated based on the hash sums of the individual input files.
        This property provides a convenient way to check if the input data has changed.

        Returns:
        ---------
        hsum: str
            The SHA256 hash sum of all input files within the Bundesland's input path.
        
        """
        # get filenames in input_path directory
        fnames = glob.glob(f"{self.output_path}/*")

        # sort filenames
        fnames = sorted(fnames)

        # get hash sum dictionary for files in input_path 
        out = self.gethash(fnames)

        # calculate hash sum of hash sum dictionary
        hsum = hashlib.sha256(str(out).encode()).hexdigest()

        return hsum


    @classmethod
    def gethash(cls, fnames: List[str]) -> dict:
        """
        Get the SHA256 hash sum for a given list of data.

        This method calculates the SHA256 hash sum for each file specified in the provided 
        list fnames.
        The hash sum provides a convenient way to check if the data has changed.


        Parameter
        ---------
        fnames: list
            List of filenames to calculate the hash sum for. 
        
        Returns
        -------
        out: dict
            Dictionary mapping files to their corresponding SHA256 hash sums.
        
        """
        # sort filenames alphabetically
        fnames = sorted(fnames)

        out = {}

        for fname in fnames:
            # exclude directories
            if os.path.isdir(fname):
                continue
            
            # open the file
            with open(fname, 'rb') as f:
                fstream = io.BytesIO()
                fstream.write(f.read())
                fstream.seek(0)
            
            # calculate hash sum for file content
            hsum = hashlib.sha256(fstream.read()).hexdigest()

            # store hash sum to output dictionary
            out[fname] = hsum

        return out


class Station():
    """
    Class for handling station data and metadata.

    """
    def __init__(self, camels_id: str):
        """
        Parameters
        ----------
        camels_od : str
            The station id of the station to be handled.
        """
        # set the station id
        # get the mapping
        mapping = get_full_nuts_mapping(format='csv')

        # check if camels_id is actually a camels_id or a provider_id
        if camels_id in mapping.provider_id.values:
            provider_id = camels_id
            camels_id = mapping.set_index('provider_id').loc[provider_id, 'nuts_id']
            warnings.warn(f"{provider_id} is a provider_id and not a CAMELS-DE NUTSID. provider_id might have duplicates, using the first one: {camels_id}")

        self.camels_id = camels_id

        # get and set the Bundesland
        self.bl = Bundesland(camels_id[0:3])

        # metadata
        meta = self.bl.metadata
        self.metadata = meta[meta.camels_id == camels_id]

        # name
        self.name = self.metadata.gauge_name.values[0]

        # location
        self.lat = self.metadata.lat.values[0]
        self.lon = self.metadata.lon.values[0]
        
        # set the output path
        self.output_path = os.path.join(self.bl.output_path, camels_id)

        # set the data path if data was already generated, else set to None
        if os.path.exists(os.path.join(self.output_path, f'{camels_id}_data.csv')):
            self.data_path = os.path.join(self.output_path, f'{camels_id}_data.csv')
        else:
            self.data_path = None

        # set the merit hydro path if data was already generated, else set to None
        if os.path.exists(os.path.join(self.output_path, f'{camels_id}_merit_hydro_catchment.geojson')):
            self.merit_hydro_path = os.path.join(self.output_path, f'{camels_id}_merit_hydro_catchment.geojson')
        else:
            self.merit_hydro_path = None

        # set the basis ezg path if data was already generated, else set to None
        if os.path.exists(os.path.join(self.output_path, f'{camels_id}_basis_ezg_catchment.geojson')):
            self.basis_ezg_path = os.path.join(self.output_path, f'{camels_id}_basis_ezg_catchment.geojson')
        else:
            self.basis_ezg_path = None

        # get the nuts mapping
        self.nuts_table = self.bl.nuts_table[self.bl.nuts_table.nuts_id == camels_id]


    def get_data(self, date_index: bool = True) -> pd.DataFrame:
        """
        Read the data from the output folder and return as pandas dataframe.
        Pass the CAMELS-DE nuts_id. 
        If date_index is False, 'date' will be a
        data column and a generic range-index is used.

        """
        # read in
        df = pd.read_csv(self.data_path, parse_dates=['date'], dtype={'q': float, 'q_flag': 'boolean', 'w': float, 'w_flag': 'boolean'})

        if date_index:
            df.set_index('date', inplace=True)
        
        return df
    

    def save_catchment_geometry(self, catchment_geometry: gpd.GeoDataFrame, datasource: str, if_exists: str = 'raise') -> str:
        """
        Save the catchment geometry to the output folder.

        Parameters
        ----------
        catchment_geometry : geopandas.GeoDataFrame
            geopandas.GeoDataFrame with the geometry for the catchment of the 
            station, which will be saved as a geojson in the output folder.
        datasource : str
            The datasource of the geometry. Can be 'merit_hydro' or 'basis_ezg'.
        if_exists : str
            The policy to handle existing files. Can be 'raise' or 'replace'.
        
        Returns
        -------
        path : str
            The path to the saved file.

        """
        # check datasource
        if datasource not in ['merit_hydro', 'basis_ezg']:
            raise ValueError(f"datasource must be either 'merit_hydro' or 'basis_ezg', but is {datasource}")
        
        # check catchment_geometry
        if not isinstance(catchment_geometry, gpd.GeoDataFrame):
            raise ValueError("catchment_geometry is not a GeoDataFrame")
        else:
            # check that only one row is included
            if len(catchment_geometry) != 1:
                raise ValueError(f"catchment_geometry contains {len(catchment_geometry)} geometries / rows for the station, 1 is allowed")

        # get the nuts mapping
        camels_id = self.camels_id

        # generate the save file name
        fname = f"{camels_id}_{datasource}_catchment.geojson"
        
        # generate the save path
        spath = os.path.abspath(os.path.join(self.output_path, fname))

        # check if there is already data
        if os.path.exists(spath):
            if if_exists == 'raise':
                raise FileExistsError(f"{spath} already exists and if_exists policy is 'raise'")
            elif if_exists == 'replace':
                pass
            else:
                raise ValueError(f"if_exists must be either 'raise' or 'replace', but is {if_exists}")
        
        # save geojson the file
        elif isinstance(catchment_geometry, gpd.GeoDataFrame):
            catchment_geometry.to_file(spath, driver='GeoJSON')

        return spath
    