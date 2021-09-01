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
    reref_param = feature_params["reref_raw"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # reref the data
        reref_eeg, output_dict = pre.reref_raw(eeg_obj, **reref_param)

        # assert that None does not exist in final reject
        assert None not in output_dict.values()

        # assert object returned is epoch object
        assert isinstance(reref_eeg, Epochs)


def test_except_value(error_obj):
    eeg_obj = error_obj

    # attempt to reref w/invalid data
    _, output_dict = pre.reref_raw(eeg_obj)
    assert isinstance(output_dict, dict)
