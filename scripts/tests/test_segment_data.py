from scripts.preprocess import preprocess as pre
from mne import Epochs


def test_return_values(default_params, bids_test_data):
    # get the pipeline steps and seg params
    feature_params = default_params["preprocess"]
    seg_param = feature_params["segment_data"]

    eeg_obj = bids_test_data

    # segment data
    seg_epo, _ = pre.segment_data(eeg_obj, **seg_param)

    # assert that data is valid
    assert isinstance(seg_epo, Epochs)
