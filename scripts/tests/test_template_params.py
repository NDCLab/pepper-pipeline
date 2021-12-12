from scripts.data import write
import pytest

import json
import os

from scripts.constants import CONFIG_FILE_NAME


@pytest.fixture
def write_path():
    dn = "test"
    if os.path.isdir(dn):
        os.rmdir(dn)
    os.mkdir(dn)
    return dn


@pytest.fixture
def default_params_write(default_params, tmp_path, write_path):
    root = default_params["load_data"]["root"]
    default_param = write.write_template_params(str(root), str(tmp_path),
                                                to_file=write_path)
    return default_param


def test_write(default_params_write, write_path):
    # check if file has been written
    for _, dirnames, filenames in os.walk(write_path):
        if not dirnames:
            assert len(filenames) == 1
    # assert that the written file is the same as user_params
    full_path = os.path.join(write_path, CONFIG_FILE_NAME)
    with open(full_path) as fp:
        written_params = json.load(fp)
    assert default_params_write == written_params

    # remove temp directory
    os.remove(full_path)
    os.rmdir(write_path)
