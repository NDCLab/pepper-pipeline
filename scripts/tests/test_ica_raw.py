from scripts.preprocess import preprocess as pre
from scripts.data import load, write

import pytest
import mne_bids

from pathlib import Path


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
def error_mnt():
    return "Fake_Montage"


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_param, sel_subjects, sel_tasks):

    default_param["load_data"]["subjects"] = sel_subjects
    default_param["load_data"]["tasks"] = sel_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the pipeline steps
    feature_params = default_param["preprocess"]
    ica_param = feature_params["ica_raw"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # reject epochs
        _, output_dict = pre.ica_raw(eeg_obj, **ica_param)

        # assert that None does not exist in bad chans
        assert None not in output_dict.values()


def test_except_bad_object(default_param, error_obj):
    feature_params = default_param["preprocess"]
    ica_param = feature_params["ica_raw"]

    # attempt to process ica w/invalid data
    _, output_dict = pre.ica_raw(error_obj, **ica_param)
    assert isinstance(output_dict, dict)


def test_except_bad_montage(default_param, sel_subjects, sel_tasks, error_mnt):
    default_param["load_data"]["subjects"] = sel_subjects
    default_param["load_data"]["tasks"] = sel_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # attempt to run ica_raw w/invalid montage
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        _, output_dict = pre.ica_raw(eeg_obj, error_mnt)
        assert isinstance(output_dict, dict)
