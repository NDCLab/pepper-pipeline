from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw


def test_return_values(default_params, bids_test_data):
    # # get default pipeline params
    feature_params = default_params["preprocess"]

    montage_params = feature_params["set_montage"]
    filt_params = feature_params["filter_data"]
    bchan_params = feature_params["identify_badchans_raw"]

    # Set the montage file
    eeg_obj, _ = pre.set_montage(bids_test_data, **montage_params)
    # filter to generate valid epoch events
    filt_obj, _ = pre.filter_data(eeg_obj, **filt_params)

    # reject epochs
    badchan_obj, _ = pre.identify_badchans_raw(filt_obj, **bchan_params)

    # assert that None does not exist in bad chans
    assert isinstance(badchan_obj, BaseRaw)
