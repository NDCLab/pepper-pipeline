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
def default_params(root):
    default_param = write.write_template_params(root)
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

    # get the pipeline steps and seg params
    feature_params = select_data_params["preprocess"]
    seg_param = feature_params["segment_data"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # segment data
        seg_epo, output_dict = pre.segment_data(eeg_obj, **seg_param)

        # assert that data is valid
        assert None not in output_dict.values()
        assert isinstance(seg_epo, Epochs)


def test_except_value(select_data_params, error_obj):
    # get the pipeline steps and seg params
    feature_params = select_data_params["preprocess"]
    seg_param = feature_params["segment_data"]

    # attempt to segment epochs with invalid epoch object
    with pytest.raises(TypeError):
        _, _ = pre.segment_data(error_obj, **seg_param)
