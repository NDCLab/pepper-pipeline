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


def test_return_values(default_param, select_subjects, select_tasks):

    default_param["load_data"]["subjects"] = select_subjects
    default_param["load_data"]["tasks"] = select_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the pipeline steps and seg params
    feature_params = default_param["preprocess"]
    seg_param = feature_params["segment_data"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # segment data
        seg_epo, output_dict = pre.segment_data(eeg_obj, **seg_param)

        # assert that None does not exist in final reject
        assert None not in output_dict.viewvalues()

        # assert object returned is epoch object
        assert isinstance(seg_epo, Epochs)


def test_except_value(default_param):
    eeg_obj = None

    # get the pipeline steps and seg params
    feature_params = default_param["preprocess"]
    seg_param = feature_params["segment_data"]

    # attempt to segment epochs with invalid epoch object
    with pytest.raises(Exception):
        _, output_dict = pre.segment_data(eeg_obj, **seg_param)
        assert True

        assert isinstance(output_dict, dict)
