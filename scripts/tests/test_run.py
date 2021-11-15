import pytest
import os
import mne

from run import run_pipeline
from scripts.preprocess import preprocess as pre
from scripts.constants import INTERM, FINAL


@pytest.fixture(params=['preloaded_data', 'non_preloaded_data'])
def single_event_epoch_data(request, default_params, raw_data):
    # Get montage and segment params
    feature_params = default_params["preprocess"]
    seg_params = feature_params["segment_data"]
    montage_param = feature_params["set_montage"]

    # Set the montage file
    eeg_obj, _ = pre.set_montage(raw_data, **montage_param)

    # Generate epoch object
    epo, _ = pre.segment_data(eeg_obj, **seg_params)

    # Get sfreq and event metadata
    s_freq = epo.info["sfreq"]
    events = epo.events
    event_id = epo.event_id

    # Convert events to annotations from epoch events
    annotate = mne.annotations_from_events(events, sfreq=s_freq)

    # Delete all other event annotations except for first
    annotate.delete(list(range(1, annotate.__len__())))
    # Set newly deleted annotations to raw
    single_event_data = raw_data.set_annotations(annotate)
    # Generate epochs from raw containing single event
    events, event_id = mne.events_from_annotations(single_event_data)
    single_event_epo = mne.Epochs(single_event_data,
                                  events,
                                  event_id,
                                  )
    if request.param == 'preloaded_data':
        single_event_epo.load_data()

    return single_event_epo


@pytest.fixture
def none_event_data(bids_test_data):
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
