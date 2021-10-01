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
    # should be a random subject?
    return ["NDARAB793GL3"]


@pytest.fixture
def sel_tasks():
    # should be a random task?
    return ["ContrastChangeBlock1"]


@pytest.fixture
def select_data_params(default_params, sel_subjects, sel_tasks):
    default_params["load_data"]["subjects"] = sel_subjects
    default_params["load_data"]["tasks"] = sel_tasks
    return default_params


@pytest.fixture
def error_tasks():
    return ["Video1"]


@pytest.fixture
def error_obj():
    return None


def test_return_values(select_data_params):
    # Load data using the selected subjects & tasks
    data = load.load_files(select_data_params["load_data"])

    feature_params = select_data_params["preprocess"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # generate epoched object to be rejected
        epo, _ = pre.segment_data(eeg_obj, **feature_params["segment_data"])
        # reject epochs
        epo.load_data()
        rej_epo, output_dict = pre.final_reject_epoch(epo)

        # assert that data is valid
        assert None not in output_dict.values()
        assert isinstance(rej_epo, Epochs)


def test_except_bad_object(error_obj):
    # attempt to filter data w/invalid data
    _, output = pre.final_reject_epoch(error_obj)
    assert "ERROR" in output.keys()


def test_except_value(select_data_params):

    # Load data using the selected subjects & tasks
    data = load.load_files(select_data_params["load_data"])

    # get the pipeline steps
    feature_params = select_data_params["preprocess"]

    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)

        # generate epoched object to be rejected
        epo, _ = pre.segment_data(eeg_obj, **feature_params["segment_data"])

        # attempt to reject epochs with data containing only one entire epoch
        # across each channel
        _, output = pre.final_reject_epoch(epo)
        assert "ERROR" in output.keys()
