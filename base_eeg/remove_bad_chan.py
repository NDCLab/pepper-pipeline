import matplotlib.pyplot as plt 
from pathlib import Path

from mne.channels import make_standard_montage
from mne import events_from_annotations, Epochs
from mne_bids import BIDSPath, read_raw_bids

import sys

def main(): 
    # import raw data 
    bids_root = Path('BIDS')
    bids_path = BIDSPath(
        subject='NDARAB793GL3', 
        session='01', 
        task='ContrastChangeBlock1',
        run='01', 
        datatype='eeg', 
        root=bids_root
    )
    raw = read_raw_bids(bids_path)

    # set standard montage 
    montage = make_standard_montage("standard_1020")
    raw.set_montage(montage)

    # create epochs
    events, event_id = events_from_annotations(raw)
    epochs = Epochs(raw, events, event_id=event_id, preload=True)

    # Mark and list bad channels 
    remove_bad_channels(epochs, raw)

def remove_bad_channels(epochs, raw):
    """Detects and marks bad channels in "raw" data-set. Modifies in place

    Parameters
    ----------
    epochs: mne.Epochs
        Data containing segmented raw dataset into epochs
    raw: mne.io.Raw
        Data containing raw EEG data that has been initliazed pre function call

    Throws
    ----------
    "Exception" exception if "raw" is not an instance of "mne.io.Raw"
    "Exception" exception if "epochs" is not an instance of "mne.io.Raw"

    
    """
    try:
        raw.load_data()
    except TypeError:
        print("\"raw\" data must be an instance of mne.io.Raw. exiting")
        sys.exit(1)

    names = raw.ch_names
    print("rejection log:", names)

    for label in names:
        raw.drop_channels(label)

if __name__ == "__main__":
    main()
