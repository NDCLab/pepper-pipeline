#!/usr/bin/python3

import matplotlib
from pathlib import Path
import mne
import mne_bids
import PyQt5

# Read BIDS Data
bids_root = Path('eeg_matchingpennies')
bids_path = mne_bids.BIDSPath(subject='05',
                              task='matchingpennies',
                              datatype='eeg',
                              root=bids_root)
raw = mne_bids.read_raw_bids(bids_path)

bad_channels = raw.info['bads']
picks = mne.pick_channels_regexp(raw.ch_names, regexp='FC.')
raw.plot(order=picks, n_channels=len(picks))
raw.load_data()

# Construct montage for our data
ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
raw_1020 = raw.copy().set_montage(ten_twenty_montage)
raw_1020_copy = raw_1020.copy().pick_types(meg=False, eeg=True, exclude=[])

# Interpolate our data
raw_interp = raw_1020_copy.copy().interpolate_bads(reset_bads=False)

# Plot the difference of original data and interpolated data
for title, data in zip(['orig.', 'interp.'], [raw_1020_copy, raw_interp]):
    fig = data.plot(butterfly=True, color='#00000022', bad_color='r')
    fig.subplots_adjust(top=0.9)
    fig.suptitle(title, size='xx-large', weight='bold')
