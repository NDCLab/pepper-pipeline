from scripts.preprocess import preprocess as pre
from scripts.data import load, write

import pytest

from pathlib import Path

import mne_bids
from mne import Epochs


@pytest.fixture
def root():
    root = Path("CMI/rawdata")
    return root


@pytest.fixture
def default_params(root, tmp_path):
    default_param = write.write_template_params(root, tmp_path)
    return default_param


@pytest.fixture
def sel_subjects():
    return ["NDARAB793GL3"]


@pytest.fixture
def sel_tasks():
    return ["ContrastChangeBlock1"]


@pytest.fixture
def select_data_params(default_params, sel_subjects, sel_tasks):
    default_params["load_data"]["subjects"] = sel_subjects
    default_params["load_data"]["tasks"] = sel_tasks
    return default_params


@pytest.fixture
def error_obj():
    return None


def test_return_values(select_data_params):
    # Load data using the selected subjects & tasks
    data = load.load_files(select_data_params["load_data"])

    # get the pipeline steps
    feature_params = select_data_params["preprocess"]
    interp_param = feature_params["interpolate_data"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # generate epoched object to be interpolated
        epo, _ = pre.segment_data(eeg_obj, **feature_params["segment_data"])

        # interpolate data
        epo.load_data()
        interp_eeg, output_dict = pre.interpolate_data(epo, **interp_param)

        # assert that all data is valid
        assert None not in output_dict.values()
        assert isinstance(interp_eeg, Epochs)


def test_except_value(error_obj, select_data_params):
    feature_params = select_data_params["preprocess"]
    interp_param = feature_params["interpolate_data"]

    # attempt to interpolate an invalid object type
    # across each channel
    _, output = pre.interpolate_data(error_obj, **interp_param)
    assert "ERROR" in output.keys()
