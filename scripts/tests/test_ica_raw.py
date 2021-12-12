from scripts import preprocess as pre
from mne.io import BaseRaw


def test_return_values(default_params, bids_test_data):
    # get default pipeline params
    feature_params = default_params["preprocess"]

    ica_param = feature_params["ica_raw"]
    filt_param = feature_params["filter_data"]
    montage_file = feature_params["set_montage"]

    eeg_obj = bids_test_data

    # set montage
    pre.set_montage(eeg_obj, **montage_file)

    # filter to generate valid epoch events
    filt_obj, _ = pre.filter_data(eeg_obj, **filt_param)

    # apply ica to filtered eeg object
    ica_obj, _ = pre.ica_raw(filt_obj, **ica_param)

    # assert that None does not exist in bad chans
    assert isinstance(ica_obj, BaseRaw)
