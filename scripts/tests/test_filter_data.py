from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw


def test_return_values(default_params, bids_test_data):
    # get the default filter params
    feature_params = default_params["preprocess"]
    filt_param = feature_params["filter_data"]

    # Run on both preloaded and non-preloaded data
    eeg_obj = bids_test_data

    # filter data
    filt_obj, _ = pre.filter_data(eeg_obj, **filt_param)

    # assert valid output objects
    assert isinstance(filt_obj, BaseRaw)
