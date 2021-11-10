import pytest
from scripts.preprocess import preprocess as pre
from mne.io import BaseRaw


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_params, bids_test_data):
    # get the pipeline steps
    feature_params = default_params["preprocess"]
    reref_param = feature_params["reref_raw"]

    eeg_obj = bids_test_data

    # reref the data
    reref_eeg, output_dict = pre.reref_raw(eeg_obj, **reref_param)

    # assert that all data is valid
    assert "ERROR" not in output_dict.values()
    assert isinstance(reref_eeg, BaseRaw)


def test_except_value(error_obj):
    eeg_obj = error_obj

    # attempt to reref w/invalid data
    _, output = pre.reref_raw(eeg_obj)
    assert "ERROR" in output.keys()
