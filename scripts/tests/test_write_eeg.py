from scripts.data import write, load

import pytest

from pathlib import Path
import os

import mne_bids


@pytest.fixture
def root():
    root = Path("CMI/rawdata")
    return root


@pytest.fixture
def default_params(root):
    default_param = write.write_template_params(root)
    return default_param


@pytest.fixture
def overwrite_params(default_params):
    default_params["load_data"]["rewrite"] = False
    return default_params


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
def write_root(tmp_path):
    temp_path = str(tmp_path) + "CMI"
    os.mkdir(temp_path)
    return temp_path


@pytest.fixture
def tmp_func():
    return "TEMP"


def test_write(select_data_params, write_root, tmp_func):
    data_params = select_data_params["load_data"]

    ch_type = data_params["channel-type"]
    rewrite = data_params["overwrite"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        write.write_eeg_data(eeg_obj, tmp_func, file, ch_type, 0, write_root,
                             rewrite)
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1


def test_overwrite(select_data_params, write_root, tmp_func):
    data_params = select_data_params["load_data"]

    ch_type = data_params["channel-type"]
    rewrite = data_params["overwrite"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        write.write_eeg_data(eeg_obj, tmp_func, file, ch_type, 0, write_root,
                             rewrite)
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1
