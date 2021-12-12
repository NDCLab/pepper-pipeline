from scripts import preprocess as pre
from mne import Epochs


def test_return_values(default_params, bids_test_epoch_data):
    # get interpolate params
    feature_params = default_params["preprocess"]
    interp_params = feature_params["interpolate_data"]

    epoch_data = bids_test_epoch_data
    interp_eeg, _ = pre.interpolate_data(epoch_data, **interp_params)

    # assert that all data is valid
    assert isinstance(interp_eeg, Epochs)
