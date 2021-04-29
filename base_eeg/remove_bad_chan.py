import matplotlib.pyplot as plt 
from pathlib import Path 

from mne.channels import make_standard_montage
from mne import events_from_annotations, Epochs
from mne_bids import BIDSPath, read_raw_bids

from faster import faster_bad_channels

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
    # montage = make_standard_montage("standard_1020")
    # raw.set_montage(montage)

    events, event_id = events_from_annotations(raw)
    epochs = Epochs(raw, events, event_id=event_id, preload=True)

    # Mark and list bad channels 
    bad_channels = faster_bad_channels(epochs)
    print(bad_channels)

if __name__ == "__main__":
    main()
