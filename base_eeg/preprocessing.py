import mne
import os
from mne_bids import write_raw_bids
"""
    Wrapper function to read data from EEG devices as a raw object dependent on
    raw binary's type. Can be extended to include several eeg data types, such
    as BrainVision and EGI. For .mff files, will convert from mff > fif,
    which will then be used for a BIDSPath.
"""


def read_raw(fname: str) -> mne.io.Raw:
    _, ext = os.path.splitext(fname)
    if(ext == ".mff"):
        raw = mne.io.read_raw_egi(fname, preload=True, verbose=True)
        raw.save("raw.fif", overwrite=True)
        return mne.io.read_raw("raw.fif")
    elif (ext == ".fif"):
        return mne.io.read_raw_fif(fname)
    else:
        pass


def write_bids(raw, bids_path):
    return write_raw_bids(
        raw,
        bids_path,
        verbose=True,
        overwrite=True
    )
