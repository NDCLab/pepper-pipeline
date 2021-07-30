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
    # should be a random subject?
    return ["NDARAB793GL3"]


@pytest.fixture
def select_tasks():
    # should be a random task?
    return ["ContrastChangeBlock1"]


@pytest.fixture
def error_tasks():
    return ["Video1"]


def test_return_values(default_param, select_subjects, select_tasks):

    default_param["load_data"]["subjects"] = select_subjects
    default_param["load_data"]["tasks"] = select_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the pipeline steps
    feature_params = default_param["preprocess"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # generate epoched object to be rejected
        epo, _ = pre.segment_data(eeg_obj, **feature_params["segment_data"])
        # reject epochs
        rej_epo, output_dict = pre.final_reject_epoch(epo)

        # assert that None does not exist in final reject
        assert None not in output_dict.viewvalues()

        # assert object returned is epoch object
        assert isinstance(rej_epo, Epochs)


def test_except_value(default_param, select_subjects, error_tasks):

    default_param["load_data"]["subjects"] = select_subjects
    default_param["load_data"]["tasks"] = error_tasks

    # Load data using the selected subjects & tasks
    data = load.load_files(default_param["load_data"])

    # get the pipeline steps
    feature_params = default_param["preprocess"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # generate epoched object to be rejected
        epo, _ = pre.segment_data(eeg_obj, **feature_params["segment_data"])

        # attempt to reject epochs with data containing only one entire epoch
        # across each channel
        with pytest.raises(ValueError):
            _, _ = pre.final_reject_epoch(epo)
            assert True
