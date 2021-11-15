from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw


def test_return_values(default_params, bids_test_data):
    # get the pipeline steps
    feature_params = default_params["preprocess"]
    reref_param = feature_params["reref_raw"]

    eeg_obj = bids_test_data

    # reref the data
    reref_eeg, output_dict = pre.reref_raw(eeg_obj, **reref_param)

    # assert that all data is valid
    assert isinstance(reref_eeg, BaseRaw)
