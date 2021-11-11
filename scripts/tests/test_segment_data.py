import pytest
from scripts.preprocess import preprocess as pre
from mne import Epochs

from scripts.constants import ERROR_KEY


@pytest.fixture
def none_event_data(bids_test_data):
    none_event_data = bids_test_data.copy().set_annotations(None)
    return none_event_data


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_params, bids_test_data):
    # get the pipeline steps and seg params
    feature_params = default_params["preprocess"]
    seg_param = feature_params["segment_data"]

    eeg_obj = bids_test_data

    # segment data
    seg_epo, output_dict = pre.segment_data(eeg_obj, **seg_param)

    # assert that data is valid
    assert ERROR_KEY not in output_dict.values()
    assert isinstance(seg_epo, Epochs)


def test_bad_object(default_params, error_obj):
    # get the pipeline steps and seg params
    feature_params = default_params["preprocess"]
    seg_param = feature_params["segment_data"]

    # attempt to segment epochs with invalid epoch object
    _, output = pre.segment_data(error_obj, **seg_param)
    assert ERROR_KEY in output.keys()


def test_no_event(default_params, none_event_data):
    # Get the default parameters for segmenting
    feature_params = default_params["preprocess"]
    seg_params = feature_params["segment_data"]

    # Run on both preloaded and non-preloaded data
    eeg_obj = none_event_data

    # generate epoched object to be rejected
    epo, _ = pre.segment_data(eeg_obj, **seg_params)

    # attempt to reject epochs with data containing no events
    _, output = pre.final_reject_epoch(epo)
    assert ERROR_KEY in output.keys()
