
import pytest
from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_params, bids_test_data):
    # get default pipeline params
    feature_params = default_params["preprocess"]

    ica_param = feature_params["ica_raw"]
    filt_param = feature_params["filter_data"]
    montage_file = feature_params["set_montage"]

    eeg_obj = bids_test_data

    # set montage
    pre.set_montage(eeg_obj, **montage_file)

    # filter
    filt_obj, _ = pre.filter_data(eeg_obj, **filt_param)

    # apply ica to filtered eeg object
    ica_obj, output_dict = pre.ica_raw(filt_obj, **ica_param)

    # assert that None does not exist in bad chans
    assert None not in output_dict.values()
    assert isinstance(ica_obj, BaseRaw)


def test_bad_object(default_params, error_obj):
    feature_params = default_params["preprocess"]
    ica_param = feature_params["ica_raw"]

    # attempt to process ica w/invalid data
    _, output = pre.ica_raw(error_obj, **ica_param)
    assert "ERROR" in output.keys()


def test_missing_montage(default_params, bids_test_data, error_obj):
    # get default pipeline params
    feature_params = default_params["preprocess"]

    ica_param = feature_params["ica_raw"]
    filt_param = feature_params["filter_data"]

    eeg_obj = bids_test_data

    # filter
    filt_obj, _ = pre.filter_data(eeg_obj, **filt_param)

    # apply ica to raw filt object with no montage file
    _, output = pre.ica_raw(filt_obj, **ica_param)

    # attempt to process ica w/invalid data
    assert "ERROR" in output.keys()
