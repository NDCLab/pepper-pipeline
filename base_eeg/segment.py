#!/usr/bin/python3
import mne
from pathlib import Path
from mne_bids import BIDSPath, read_raw_bids

# Read BIDS data
bids_root = Path('eeg_matchingpennies')
bids_path = BIDSPath(subject='05',
                     task='matchingpennies',
                     datatype='eeg',
                     root=bids_root)
raw = read_raw_bids(bids_path)

# extract events and event_id from our raw object
events, event_id = mne.events_from_annotations(raw)

# we can go ahead and plot the events
mne.viz.plot_events(events, event_id=event_id)

# create an epoch object and we can extract information off of it
epochs = mne.Epochs(raw, events, event_id=event_id, preload=True)
epochs.plot(n_epochs=10)
print(epochs.info)
print(epochs[['left', 'right']])
