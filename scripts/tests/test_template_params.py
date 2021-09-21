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
def default_params(root, tmp_path):
    default_param = write.write_template_params(root, tmp_path)
    return default_param


@pytest.fixture
def default_params_write(root, tmp_path):
    default_param = write.write_template_params(root, tmp_path,
                                                to_file=tmp_path / "test.json")
    return default_param


@pytest.fixture
def load_data_params():
    return ["root", "subjects", "tasks", "exceptions", "channel-type", 
            "exit_on_error", "overwrite", "parallel"]


@pytest.fixture
def preprocess_params():
    return ["filter_data", "identify_badchans_raw", "ica_raw", "segment_data",
            "final_reject_epoch-type", "interpolate_data", "reref_raw",
            "parallel"]


@pytest.fixture
def output_data_params():
    return ["root"]


def test_params(default_params):
    load_data = default_params["load_data"]
    preprocess =  default_params["preprocess"]
    output_data = default_params["output_data"]

    
