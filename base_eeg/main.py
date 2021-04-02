#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author = "Jonhas Colina and Dan Roberts"
@license = "LGPL"
Main scripting file for the preprocessing system
"""

import preprocessing
from mne_bids import BIDSPath
import argparse
import mne
import sys

if __name__ == "__main__":
    # Argument parser object to allow passing of command line args
    parser = argparse.ArgumentParser(
        description="Preprocessing Script for EEG Data"
    )

    parser.add_argument(
        '--fname',
        help="Path to raw EGI file",
        type=str,
    )

    args = parser.parse_args()
    if not args.fname:
        parser.print_usage()
        sys.exit(1)

    raw = preprocessing.read_raw(args.fname)

    # Use the aggregate stimulation channel 'STI 014' to create
    # an events structure
    events = mne.find_events(raw, stim_channel="STI 014", shortest_event=1)
    event_annotations = mne.annotations_from_events(
        events=events,
        sfreq=raw.info['sfreq'],
        orig_time=raw.info['meas_date']
    )

    # add annotations to existing annotations (the bad acquisition skips)
    # and keep only the EEG channels, removing the stimulation channels
    raw.set_annotations(raw.annotations + event_annotations)
    raw.pick_types(eeg=True)

    # Building the BidsPath which allows dynamic updating of entities in place
    bids_path = BIDSPath(
        subject="01",
        session="01",
        task="testing",
        run="01",
        root="~/"
    )

    # PowerLineFrequency parameter is required in the sidecar files.
    raw.info['line_freq'] = 60

    bids = preprocessing.write_bids(raw, bids_path)
