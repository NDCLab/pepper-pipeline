from scripts.data import write, load
from scripts import preprocess as pre

import pytest
import os

import mne_bids


@pytest.fixture
def non_path_params(default_params, tmp_path):
    default_params["output_root"] = tmp_path / "CMI"
    return default_params


@pytest.fixture
def overwrite_params(default_params):
    default_params["load_data"]["overwrite"] = False
    return default_params


def test_write(default_params):
    data_params = default_params["load_data"]

    write_root = data_params["output_root"]
    ch_type = data_params["channel_type"]

    # get the pipeline steps
    feature_params = default_params["preprocess"]
    filt_param = feature_params["filter_data"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        _, output_dict = pre.filter_data(eeg_obj, **filt_param)

        write.write_output_param(output_dict, file, ch_type, write_root)
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1


def test_non_path(non_path_params):
    data_params = non_path_params["load_data"]

    ch_type = data_params["channel_type"]
    write_root = data_params["output_root"]

    # get the pipeline steps
    feature_params = non_path_params["preprocess"]
    filt_param = feature_params["filter_data"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        _, output_dict = pre.filter_data(eeg_obj, **filt_param)
        # first write
        write.write_output_param(output_dict, file, ch_type, write_root)
        # assert file exists even if path initially does not
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1
