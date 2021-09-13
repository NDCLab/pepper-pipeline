from scripts.preprocess import preprocess as pre
from scripts.data import load, write

import pytest

from pathlib import Path

import mne_bids


@pytest.fixture
def root():
    root = Path("CMI/rawdata")
    return root


@pytest.fixture
def default_param(root):
    default_param = write.write_template_params(root)
    return default_param


@pytest.fixture
def sel_subjects():
    return ["NDARAB793GL3"]


@pytest.fixture
def sel_tasks():
    return ["ContrastChangeBlock1"]


@pytest.fixture
def error_obj():
    return None


@pytest.fixture
def error_val():
    return 1.0


def test_return_values(default_param, sel_subjects, sel_tasks):

    default_param["load_data"]["subjects"] = sel_subjects
    default_param["load_data"]["tasks"] = sel_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the pipeline steps
    feature_params = default_param["preprocess"]
    filt_param = feature_params["filter_data"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # filter data
        _, output_dict = pre.filter_data(eeg_obj, **filt_param)

        # assert that None does not exist in final reject
        assert None not in output_dict.values()


def test_except_bad_object(error_obj):
    # attempt to filter data w/invalid data
    _, output_dict = pre.filter_data(error_obj)
    assert isinstance(output_dict, dict)


def test_except_bad_params(default_param, sel_subjects, sel_tasks, error_val):

    default_param["load_data"]["subjects"] = sel_subjects
    default_param["load_data"]["tasks"] = sel_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # filter data
        _, output_dict = pre.filter_data(eeg_obj, error_val, error_val)
        assert isinstance(output_dict, dict)
