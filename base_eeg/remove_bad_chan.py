import matplotlib
import pathlib
import mne
import mne_bids
import autoreject as ar 

import logging
import sys
import os 
import json 

def main(): 
    # import raw data 
    bids_root = pathlib.Path('BIDS')
    bids_path = mne_bids.BIDSPath(
        subject='NDARAB793GL3', 
        session='01', 
        task='ContrastChangeBlock1',
        run='01', 
        datatype='eeg', 
        root=bids_root
    )
    raw = mne_bids.read_raw_bids(bids_path)
    montage = mne.channels.make_standard_montage("standard_1020")
    raw.set_montage(montage)

    # Mark and list bad channels 
    # remove_bad_channels(epochs, raw)

def remove_bad_channels(epochs: mne.Epochs, raw: mne.io.Raw) -> None:
    """Automatically detect bad channels and mark to ignore during analysis 

    @ modifies: raw 
    @ throws: 
        - "Exception" exception if "raw" is not an instance of "mne.io.Raw"
    @ postconditions: bad channels are annotated as such within "raw" dataset 
    """
    try:
        raw.load_data()
    except Exception:
        print("\"raw\" data must be an instance of mne.io.Raw. exiting")
        sys.exit(1)

    # Init logging file to record warnings and errors
    logging.basicConfig(filename='output.log', filemode='a', level=logging.NOTSET)

    reject = ar.AutoReject()
    reject.fit(epochs)
    reject_log = reject.get_reject_log(epochs)

    names = reject_log.ch_names
    print("rejection log:", names)

    for label in names:
        raw.drop_channels(label)

if __name__ == "__main__":
    main()
