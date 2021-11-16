import pytest
import os
import mne

from run import run_pipeline
from scripts.constants import INTERM, FINAL


@pytest.fixture
def single_event_data(bids_test_data):
    # Get sfreq and event metadata
    s_freq = bids_test_data.info["sfreq"]
    events = bids_test_data.events

    # Convert events to annotations from epoch events
    annotate = mne.annotations_from_events(events, sfreq=s_freq)

    # Delete all other event annotations except for first
    annotate.delete(list(range(1, annotate.__len__())))
    # Set newly deleted annotations to raw
    single_event_data = bids_test_data.copy().set_annotations(annotate)

    return single_event_data


@pytest.fixture
def no_event_data(bids_test_data):
    none_event_data = bids_test_data.copy().set_annotations(None)
    return none_event_data


def test_default_pipeline(default_params, tmp_path):
    # get the default params
    preprocess_params = default_params["preprocess"]
    load_params = default_params["load_data"]
    write_params = default_params["output_data"]

    run_pipeline(preprocess_params, load_params, write_params)

    # assert data is written in tmp_path
    for _, dirnames, filenames in os.walk(tmp_path):
        if dirnames == INTERM:
            # if at interm dir, assert all but final obj written
            assert len(filenames) == len(preprocess_params) - 1
        elif dirnames == FINAL:
            # if at final dir, assert final obj written
            assert len(filenames) == 1
