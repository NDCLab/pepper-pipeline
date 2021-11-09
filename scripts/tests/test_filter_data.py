import pytest
from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw


@pytest.fixture
def error_obj():
    return None


@pytest.fixture
def error_val():
    return 1.0


def test_return_values(default_params, bids_test_data):
    # get the default filter params
    feature_params = default_params["preprocess"]
    filt_param = feature_params["filter_data"]

    # Run on both preloaded and non-preloaded data
    eeg_obj = bids_test_data

    # filter data
    filt_obj, output_dict = pre.filter_data(eeg_obj, **filt_param)

    # assert valid output objects
    assert "ERROR" not in output_dict.keys()
    assert isinstance(filt_obj, BaseRaw)


def test_bad_object(error_obj):
    # attempt to filter data w/invalid data
    _, output = pre.filter_data(error_obj)
    assert "ERROR" in output.keys()


def test_bad_params(bids_test_data, error_val):
    # Run on both preloaded and non-preloaded data
    eeg_obj = bids_test_data

    # filter data using erroneous parameters
    _, output = pre.filter_data(eeg_obj, error_val, error_val)
    assert "ERROR" in output.keys()
