import pytest
from scripts.data import write, load

import os
import mne_bids


@pytest.fixture
def overwrite_params(default_params):
    default_params["load_data"]["overwrite"] = False
    return default_params


@pytest.fixture
def non_path_params(default_params, tmp_path):
    default_params["output_data"]["root"] = tmp_path / "CMI"
    return default_params


@pytest.fixture
def tmp_func():
    return "TEMP"


def test_write(default_params, tmp_func):
    data_params = default_params["load_data"]
    output_params = default_params["output_data"]

    ch_type = data_params["channel-type"]
    rewrite = data_params["overwrite"]
    write_root = output_params["root"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        write.write_eeg_data(eeg_obj, tmp_func, file, ch_type, 0, write_root,
                             rewrite)
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1


def test_overwrite(default_params, tmp_func):
    data_params = default_params["load_data"]
    output_params = default_params["output_data"]

    ch_type = data_params["channel-type"]
    rewrite = data_params["overwrite"]
    write_root = output_params["root"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        # first write
        first_write = write.write_eeg_data(eeg_obj, tmp_func, file,
                                           ch_type, 0, write_root, rewrite)
        # overwrite
        overwrite = write.write_eeg_data(eeg_obj, tmp_func, file,
                                         ch_type, 0, write_root, rewrite)

        # assert first write produced string and second produced string again
        assert isinstance(first_write, str) and isinstance(overwrite, str)


def test_non_overwrite(overwrite_params, tmp_func):
    data_params = overwrite_params["load_data"]
    output_params = overwrite_params["output_data"]

    ch_type = data_params["channel-type"]
    rewrite = data_params["overwrite"]
    write_root = output_params["root"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        # first write
        first_write = write.write_eeg_data(eeg_obj, tmp_func, file,
                                           ch_type, 0, write_root, rewrite)
        # overwrite
        overwrite = write.write_eeg_data(eeg_obj, tmp_func, file,
                                         ch_type, 0, write_root, rewrite)

        # assert first write produced string and second produced string again
        assert isinstance(first_write, str) and (overwrite is None)


def test_non_path(non_path_params, tmp_func):
    data_params = non_path_params["load_data"]
    output_params = non_path_params["output_data"]

    ch_type = data_params["channel-type"]
    rewrite = data_params["overwrite"]
    write_root = output_params["root"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        # first write
        write.write_eeg_data(eeg_obj, tmp_func, file,
                             ch_type, 0, write_root, rewrite)
        # assert file exists even if path initially does not
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1
