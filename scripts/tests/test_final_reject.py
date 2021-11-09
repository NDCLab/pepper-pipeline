import pytest
from scripts.preprocess import preprocess as pre
import mne


@pytest.fixture
def single_event_epoch_data(default_params, bids_test_data):
    # Get the default parameters for segmenting
    feature_params = default_params["preprocess"]
    seg_params = feature_params["segment_data"]
    montage_param = feature_params["set_montage"]

    # Get events and sampling frequency
    events, _ = mne.events_from_annotations(bids_test_data)
    s_freq = bids_test_data.info["sfreq"]

    # Convert events to annotations
    annotate = mne.annotations_from_events(events, sfreq=s_freq)

    # Limit annotations to single event and set
    annotate.delete(list(range(1, annotate.__len__())))
    single_event_data = bids_test_data.copy().set_annotations(annotate)

    # Run on both preloaded and non-preloaded data
    eeg_obj = single_event_data

    # Set the montage file
    eeg_obj, _ = pre.set_montage(eeg_obj, **montage_param)

    # generate epoched object to be rejected
    epo, _ = pre.segment_data(eeg_obj, **seg_params)

    return epo


@pytest.fixture
def epoch_data(default_params, bids_test_data):
    # Get montage and segment params
    feature_params = default_params["preprocess"]
    seg_params = feature_params["segment_data"]
    montage_param = feature_params["set_montage"]

    # Run on both preloaded and non-preloaded data
    eeg_obj = bids_test_data

    # Set the montage file
    eeg_obj, _ = pre.set_montage(eeg_obj, **montage_param)

    # Generate epoched object to be rejected
    epo, _ = pre.segment_data(eeg_obj, **seg_params)

    return epo


@pytest.fixture
def error_obj():
    # Maybe this should eventually become a busted EEG file
    return None


def test_return_values(epoch_data):
    # Reject epochs using ar
    rej_epo, output_dict = pre.final_reject_epoch(epoch_data)

    # assert that data is valid
    assert "ERROR" not in output_dict.keys()
    assert isinstance(rej_epo, mne.Epochs)


def test_bad_object(error_obj):
    # attempt to filter data w/invalid data
    _, output = pre.final_reject_epoch(error_obj)
    assert "ERROR" in output.keys()


def test_single_event(single_event_epoch_data):
    # attempt to reject epochs with data containing only one entire epoch
    # across each channel
    _, output = pre.final_reject_epoch(single_event_epoch_data)
    assert "ERROR" in output.keys()
