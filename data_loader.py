from scipy.io import loadmat
import numpy as np
import pandas as pd

from utils import pad, find_segments
from config import DRUG_ABBR
    
class EEGDataLoader:
    """ ECoG data loader and accessor
    (the data are assumed to be stored as .mat files)
    
    """
    
    def __init__(self, fpaths: dict, preprocess_clean: bool = True):
        """ 
        Args:
            fpaths (dict): {drug_name: file_path}
            preprocess_clean (bool): Whether to preprocess the clean data
        """
        self.df = self._build_df(fpaths)
        if preprocess_clean:
            self.df = self._preprocess_clean(self.df)

    def _build_df(self, fpaths:dict) -> pd.DataFrame:
        """ Building a dataframe from drug ecog/eeg data that contains conlumns:
        drug_name (str), drug_abbr(str), animal_id (str), animal_idx (int), window_name (str), window_idx (int), raw (np.ndarray), clean (np.ndarray)

        where:
        - drug_name: 
        - drug_abbr: 
        - animal_id looks like "Animal1_drug1", "Animal2_drug2", etc. (fixing information dependency)
        - animal_idx is the index of the animal per drug (for easier access)
        - window_name is the name of the time window in the data (if data is splited by time windows)
        - window_idx is the index of the window in the data 
        - raw/clean is the raw/clean eeg data (stored as np.ndarray)
        
        Args:
            fpaths (dict): {drug_name: file_path}

        Returns:
            pd.DataFrame
            
        Note: the following data processing code is dependent on the structure of the input (.mat) files, 
        which is assumed to be consistent across drugs. 
        If the structure changes, this code may need to be updated accordingly.
        """
        rows = []
        # for each drug ...
        for drug, path in fpaths.items():
            drug_data = loadmat(path) # dict
            animal_keys = [k for k in drug_data.keys() if not k.startswith("__")] # get the keys that are not metadata
            # for each animal ...
            for animal_idx in range(1, len(animal_keys)+1):
                animal_id = f"Animal{animal_idx}_{drug}"
                animal_key = animal_keys[animal_idx-1]
                animal_data = drug_data[animal_key]
                # for each window ...
                for window_idx in range(animal_data.shape[1]):
                    window_data = animal_data[0, window_idx]
                    window_name = window_data['name'].item()
                    raw_data = window_data['raw'].squeeze()
                    clean_data = window_data['clean'].squeeze()
                    
                    rows.append({
                        "drug_name": drug,
                        "drug_abbr": DRUG_ABBR[drug],
                        "animal_id": animal_id,
                        "animal_idx": animal_idx,
                        "window_name": window_name,
                        "window_idx": window_idx,
                        "raw": raw_data,
                        "clean": clean_data,
                    })
        df = pd.DataFrame(rows)
        df = df.set_index(["drug_abbr", "animal_idx", "window_idx"]).sort_index()
        
        return df
    
    def _preprocess_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Pad clean data, segment data into contiguous non_NaN segments"""
        df["clean_padded"] = df.apply(lambda row: pad(row["raw"].tolist(), row["clean"].tolist()), axis=1)
        df["clean_segments"] = df["clean_padded"].apply(lambda x: [x[s:e] for s, e in find_segments(x)])
        return df

    # slice the clean data into 
    
    def query(self, drug: str, animal: int, window: int, clean: bool = True, padded: bool = True) -> np.ndarray:
        """ Query the dataframe based on drug_name, animal_id, and/or window_name.
        
        Args:
            drug (str): Name of the drug to filter by.
            animal (int): Index of the animal to filter by.
            window (int): Index of the window to filter by.
            clean (bool): Whether to return the clean data or raw data. Defaults to True.
            padded (bool): Whether to return the padded clean data or not. Defaults to True.

        Returns:
            np.ndarray: Filtered array based on the provided criteria.
        """        
        if drug is None or animal is None or window is None:
            raise ValueError("Not enough information provided.")
        col = 'clean' if clean else 'raw'
        if padded and clean:
            col = 'clean_padded'
        data = self.df.loc[(drug, animal, window), col]
        return np.asarray(data)