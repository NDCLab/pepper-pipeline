from scripts.data import write, load

import pytest

from pathlib import Path
import os

import mne_bids
import pandas as pd


@pytest.fixture
def default_param(root):
    default_param = write.write_template_params(root)
    return default_param


@pytest.fixture
def select_subj():
    return ["NDARAB793GL3"]


@pytest.fixture
def select_task():
    return ["ContrastChangeBlock1"]


@pytest.fixture
def temp_root(tmp_path):
    temp_path = str(tmp_path) + "CMI"
    os.mkdir(temp_path)


@pytest.fixture
def tmp_func():
    return "TEMP"


def test_write(default_param, select_subj, select_task, temp_root, tmp_func):
    data_params = default_param["load_data"]

    data_params["root"] = temp_root
    data_params["subjects"] = select_subj
    data_params["tasks"] = select_task

    ch_type = data_params["channel-type"]
    rewrite = data_params["rewrite"]

    data = load.load_files(default_param["load_data"])
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        write.write_eeg_data(eeg_obj, tmp_func, file, ch_type, 0, temp_root,
                             rewrite)
