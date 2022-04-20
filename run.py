import mne_bids
from scripts.data import load, write
from scripts import preprocess as pre

from collections import ChainMap
from itertools import repeat

import logging
from multiprocessing import Pool
import sys
from scripts.constants import \
    ERROR_KEY, \
    DEFAULT_LOAD_PARAMS, \
    CONFIG_FILE_NAME


def clean_outputs(output_dict):
    output_dict = [result for result in output_dict if result is not None]
    return output_dict


def preprocess_data(file, load_data, preprocess):
    """Function to preprocess data

    Parameters
    ----------
    file:   BIDSPath
            Path pointing to individual BIDS data
    load_data:  dict()
                Dictionary containing data selection and pipeline meta-params
    preprocess: dict()
                Dictionary containing preprocess params
    """
    # get pipeline parameters
    write_path = load_data["output_root"]
    ch_type = load_data["channel_type"]
    exit_on_error = load_data["exit_on_error"]
    overwrite = load_data["overwrite"]

    # load raw data from file
    eeg_obj = mne_bids.read_raw_bids(file)

    # if data has been preprocessed already, exit
    if write.check_hash(eeg_obj, load_data) and overwrite:
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
        write.write_eeg_data(eeg_obj, func, file, ch_type, final, write_path)

    # collect annotations of each step
    outputs.reverse()
    output = dict(ChainMap(*outputs))
    write.write_output_param(output, file, ch_type, write_path)


def run_preprocess(load_data, preprocess):
    """Function to take in user_params parameters to preprocess EEG data
    and potentially run in parallel.
    Writes out derivates.

    Parameters
    ----------
    load_data:  dict()
                Dictionary containing data selection and pipeline meta-params
    preprocess: dict()
                Dictionary containing preprocess features and their parameters

    """
    # Get number of workers to use for parallel runs
    p_runs = load_data["parallel_runs"]

    # get set of subjects & tasks to run while omitting existing exceptions
    data = load.load_files(load_data)

    # get number of workers based on param
    runs = p_runs if p_runs else DEFAULT_LOAD_PARAMS.parallel_runs

    # parallelize data by executing pipeline steps on each loaded file
    with Pool(runs) as worker:
        worker.starmap(preprocess_data,
                       zip(data, repeat(load_data), repeat(preprocess)))


if __name__ == "__main__":
    # load all parameters
    input_configs = load.load_params(CONFIG_FILE_NAME)

    # get data and metadata sections
    load_params = input_configs["load_data"]
    preprocess_params = input_configs["preprocess"]
    subpost_params = input_configs["subject_level_postprocess"]
    studypost_params = input_configs["study_level_postprocess"]

    # Execute pipeline steps specified in preprocess
    run_preprocess(load_params, preprocess_params)
