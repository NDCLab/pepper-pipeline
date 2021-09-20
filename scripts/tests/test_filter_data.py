from scripts.preprocess import preprocess as pre
from scripts.data import load, write

import pytest

from pathlib import Path

import mne_bids
from mne.io import BaseRaw


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


@pytest.fixture
def error_val():
    return 1.0


def test_return_values(select_data_params):
    # Load data using the selected subjects & tasks
    data = load.load_files(select_data_params["load_data"])

    # get the pipeline steps
    feature_params = select_data_params["preprocess"]
    filt_param = feature_params["filter_data"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # filter data
        filt_obj, output_dict = pre.filter_data(eeg_obj, **filt_param)

        # assert valid output objects
        assert None not in output_dict.values()
        assert isinstance(filt_obj, BaseRaw)


def test_except_bad_object(error_obj):
    # attempt to filter data w/invalid data
    with pytest.raises(TypeError):
        _, _ = pre.filter_data(error_obj)


def test_except_bad_params(select_data_params, error_val):
    # Load data using the selected subjects & tasks
    data = load.load_files(select_data_params["load_data"])

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # filter data
        with pytest.raises(ValueError):
            _, _ = pre.filter_data(eeg_obj, error_val, error_val)
