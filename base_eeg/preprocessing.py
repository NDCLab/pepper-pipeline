import mne
import os
from mne_bids import write_raw_bids
"""
    Wrapper function to read data from EEG devices as a raw object dependent on
    raw binary's type. Can be extended to include several eeg data types, such as 
    BrainVision and EGI. 
"""

def read_raw(fname: str) -> mne.io.Raw:
    _, ext = os.path.splitext(fname)
    if(ext == ".mff"):
        return mne.io.read_raw_egi(fname)
    else:
        pass 


def write_bids(raw, bids_path):
    return write_raw_bids(
        raw, 
        bids_path,
        verbose=True 
    )
