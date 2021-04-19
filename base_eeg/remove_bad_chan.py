import matplotlib
import pathlib
import mne
import mne_bids
import autoreject as ar 
import logging
import os 

def main(): 
    # import raw data 
    bids_root = pathlib.Path('base_eeg/raw_data/eegmatchingpennies')
    bids_path = mne_bids.BIDSPath(subject='05', task='matchingpennies', datatype='eeg', root=bids_root)
    raw = mne_bids.read_raw_bids(bids_path)

    # Generate events to segment data into epochs 
    events, event_id = mne.events_from_annotations(raw)
    epochs = mne.Epochs(raw, events, event_id=event_id, preload=True)

    # Set montage
    easy_montage = mne.channels.make_standard_montage('easycap-M1')
    epochs.set_montage(easy_montage)

    # Mark and list bad channels 
    remove_bad_channels(epochs, raw)

def remove_bad_channels(epochs: mne.Epochs, raw: mne.io.Raw):
    """Automatically detect bad channels and mark to ignore during analysis 

    @ preconditions: epochs specifically segments the raw dataset 
    @ modifies: raw 
    @ postconditions:
    """
    # Init logging file to record warnings and errors
    logging.basicConfig(filename='output.log', filemode='a', level=logging.NOTSET)

    reject = ar.AutoReject()

    reject.fit(epochs)
    reject_log = reject.get_reject_log(epochs)

    # TODO: ch_names currently include ALL channels 
    names = reject_log.ch_names
    print("rejection log:", names)

    for label in names:
        raw.drop_channels(label)

if __name__ == "__main__":
    main()
