import mne_bids
from scripts.data import load, write
from scripts.preprocess import preprocess as pre

from collections import ChainMap
from itertools import repeat

import logging
from multiprocessing import Pool

import sys
from scripts.constants import \
    ERROR_KEY, \
    DEFAULT_LOAD_PARAMS


def clean_outputs(output_dict):
    output_dict = [result for result in output_dict if result is not None]
    return output_dict


def preprocess_data(file, preprocess, ch_type, exit_on_error, rewrite, path):
    """Function to preprocess data
    """
    # load raw data from file
    eeg_obj = mne_bids.read_raw_bids(file)

    # if data has been preprocessed already, exit
    if write.is_preprocessed(file, ch_type, path, rewrite):
        logging.info("File already preprocessed. Skipping write according to 'rewrite'\
                      parameter.")
        return
    # initialize output list
    outputs = [None] * len(preprocess)

    # For each pipeline step, execute with parameters
    for idx, (func, params) in enumerate(preprocess.items()):
        try:
            eeg_obj, outputs[idx] = getattr(pre, func)(eeg_obj, **params)
        except Exception as e:
            # On error, replace output with exception
            outputs[idx] = {func: ERROR_KEY + str(e)}
            # Remove all un-filled outputs
            outputs = clean_outputs(outputs)

            # Exit pipeline or skip subject
            if exit_on_error:
                sys.exit("Pipeline exited according to 'exit_on_error'")
            logging.info("Exception caught in function. Skipping to next \
                          subject.")
            break

        # check if this is the final preprocessed eeg object
        final = (idx == len(preprocess.items()) - 1)
        # write object out to file
        write.write_eeg_data(eeg_obj, func, file, ch_type, final, path)

    # collect annotations of each step
    outputs.reverse()
    output = dict(ChainMap(*outputs))
    write.write_output_param(output, file, ch_type, path)


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
    ch_type = load_data["channel_type"]
    exit_error = load_data["exit_on_error"]
    rewrite = load_data["overwrite"]
    p_runs = load_data["parallel_runs"]
    path = write_data["root"]

    # get set of subjects & tasks to run while omitting existing exceptions
    data = load.load_files(load_data)

    # get number of workers based on param
    runs = p_runs if p_runs else DEFAULT_LOAD_PARAMS.parallel_runs

    # parallelize data by executing pipeline steps on each loaded file
    with Pool(runs) as worker:
        worker.starmap(preprocess_data,
                       zip(data, repeat(preprocess), repeat(ch_type),
                           repeat(exit_error), repeat(rewrite), repeat(path)))


if __name__ == "__main__":
    # load all parameters
    user_params = load.load_params("user_params.json")

    # get data and metadata sections
    preprocess_params = user_params["preprocess"]
    load_params = user_params["load_data"]
    write_params = user_params["output_data"]

    # Execute pipeline steps specified in user_params.json
    run_pipeline(preprocess_params, load_params, write_params)
