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
def default_param(root):
    default_param = write.write_template_params(root)
    return default_param


@pytest.fixture
def select_subjects():
    return ["NDARAB793GL3"]


@pytest.fixture
def select_tasks():
    return ["ContrastChangeBlock1"]


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_param, select_subjects, select_tasks):

    default_param["load_data"]["subjects"] = select_subjects
    default_param["load_data"]["tasks"] = select_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the pipeline steps
    feature_params = default_param["preprocess"]
    interp_param = feature_params["interpolate_data"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # generate epoched object to be interpolated
        epo, _ = pre.segment_data(eeg_obj, **feature_params["segment_data"])

        # interpolate data
        interp_eeg, output_dict = pre.interpolate_data(epo, **interp_param)

        # assert that None does not exist in final reject
        assert None not in output_dict.values()

        # assert object returned is epoch object
        assert isinstance(interp_eeg, Epochs)


def test_except_value(error_obj):
    eeg_obj = error_obj

    # attempt to interpolate an invalid object type
    # across each channel
    with pytest.raises(Exception):
        _, output_dict = pre.interpolate_data(eeg_obj)
        assert isinstance(output_dict, dict)
