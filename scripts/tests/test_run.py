from run import run_pipeline
import os
from scripts.constants import INTERM, FINAL


def test_default_pipeline(default_params, tmp_path):
    # get the default params
    preprocess_params = default_params["preprocess"]
    load_params = default_params["load_data"]
    write_params = default_params["output_data"]

    run_pipeline(preprocess_params, load_params, write_params)

    # assert data is written in tmp_path
    for _, dirnames, filenames in os.walk(tmp_path):
        if dirnames == INTERM:
            # if at interm dir, assert all but final obj written
            assert len(filenames) == len(preprocess_params) - 1
        elif dirnames == FINAL:
            # if at final dir, assert final obj written
            assert len(filenames) == 1
