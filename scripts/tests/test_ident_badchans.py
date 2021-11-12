import pytest
from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw

from scripts.constants import ERROR_KEY


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_params, bids_test_data):
    # # get default pipeline params
    feature_params = default_params["preprocess"]

    montage_params = feature_params["set_montage"]
    filt_params = feature_params["filter_data"]
    bparams = feature_params["identify_badchans_raw"]

    eeg_obj = bids_test_data

    # Set the montage file
    eeg_obj, _ = pre.set_montage(eeg_obj, **montage_params)
    # filter to generate valid epoch events
    filt_obj, _ = pre.filter_data(eeg_obj, **filt_params)

    # reject epochs
    badchan_obj, output_dict = pre.identify_badchans_raw(filt_obj, **bparams)

    print(output_dict)

    # assert that None does not exist in bad chans
    assert ERROR_KEY not in output_dict.keys()
    assert isinstance(badchan_obj, BaseRaw)
