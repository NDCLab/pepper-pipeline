from scripts.data import load, write
from scripts.preprocess import preprocess as pre

from scripts.postprocess.metrics import sme
from scripts.postprocess.metrics import reliability
from scripts.postprocess.measures import erp

from collections import ChainMap
import mne_bids

import logging
import traceback

import sys
from scripts.constants import \
    CAUGHT_EXCEPTION_SKIP, \
    EXIT_MESSAGE, \
    ERROR_KEY


def clean_outputs(output_dict):
    output_dict = [result for result in output_dict if result is not None]
    return output_dict


def run_pipeline(preprocess, load_data, write_data):
    """Function to take in user_params parameters to preprocess EEG data.
    Writes out derivates.

    Parameters
    ----------
    preprocess: dict()
                Dictionary containing preprocess features and their parameters
    load_data:  dict()
                Dictionary containing data selection and pipeline meta-params
    write_data: dict()
                Dictionary containing parameters to write data

    """
    # get pipeline parameters
    ch_type = load_data["channel-type"]
    exit_on_error = load_data["exit_on_error"]
    rewrite = load_data["overwrite"]
    path = write_data["root"]

    # get set of subjects & tasks to run while omitting existing exceptions
    data = load.load_files(load_data)

    # for each file in filtered data
    for file in data:
        # load raw data
        eeg_obj = mne_bids.read_raw_bids(file)
        # initialize output list
        outputs = [None] * len(preprocess)

        # For each pipeline step in user_params, execute with parameters
        for idx, (func, params) in enumerate(preprocess.items()):
            # Handle any unexpected exceptions by logging to shell and skipping
            try:
                eeg_obj, outputs[idx] = getattr(pre, func)(eeg_obj, **params)
            except Exception as e:
                logging.error(e)
                logging.info(traceback.format_exc())
                outputs = clean_outputs(outputs)
                break

            # If a caught error has been detected, log and skip
            if ERROR_KEY in outputs[idx].keys():
                logging.info(CAUGHT_EXCEPTION_SKIP)
                outputs = clean_outputs(outputs)
                # or exit if pipeline specifies
                if exit_on_error:
                    sys.exit(EXIT_MESSAGE)
                break

            # check if this is the final preprocessed eeg object
            final = (idx == len(preprocess.items()) - 1)
            # write object out to file
            write.write_eeg_data(eeg_obj, func, file, ch_type, final, path,
                                 rewrite)

        # collect annotations of each step
        outputs.reverse()
        output = dict(ChainMap(*outputs))
        write.write_output_param(output, file, ch_type, path, rewrite)


def sub_postprocess_data(postprocess):
    return postprocess


def stud_postprocess_data(postprocess):
    return postprocess


if __name__ == "__main__":
    # load all parameters
    user_params = load.load_params("user_params.json")

    # get data and metadata sections
    preprocess_params = user_params["preprocess"]
    load_params = user_params["load_data"]
    write_params = user_params["output_data"]

    # Execute pipeline steps specified in user_params.json
    run_pipeline(preprocess_params, load_params, write_params)
