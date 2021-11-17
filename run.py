from scripts.data import load, write
from scripts.preprocess import preprocess as pre

from collections import ChainMap
import mne_bids

import logging
from multiprocessing import Pool
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
    def preprocess_data(file):
        """Nested function to preprocess data
        """
        # load raw data from file
        eeg_obj = mne_bids.read_raw_bids(file)
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
                    sys.exit(EXIT_MESSAGE)
                logging.info(CAUGHT_EXCEPTION_SKIP)
                return

            # check if this is the final preprocessed eeg object
            final = (idx == len(preprocess.items()) - 1)
            # write object out to file
            write.write_eeg_data(eeg_obj, func, file, ch_type, final, path,
                                 rewrite)

        # collect annotations of each step
        outputs.reverse()
        output = dict(ChainMap(*outputs))
        write.write_output_param(output, file, ch_type, path, rewrite)

    # get pipeline parameters
    ch_type = load_data["channel-type"]
    exit_on_error = load_data["exit_on_error"]
    rewrite = load_data["overwrite"]
    parallel = load_data["parallel"]
    path = write_data["root"]

    # get set of subjects & tasks to run while omitting existing exceptions
    data = load.load_files(load_data)

    # get number of runs based on available cpus and param
    runs = 1 if parallel else None

    with Pool(runs) as worker:
        # for each file in filtered data
        worker.map(preprocess_data, data)


if __name__ == "__main__":
    # load all parameters
    user_params = load.load_params("user_params.json")

    # get data and metadata sections
    preprocess_params = user_params["preprocess"]
    load_params = user_params["load_data"]
    write_params = user_params["output_data"]

    # Execute pipeline steps specified in user_params.json
    run_pipeline(preprocess_params, load_params, write_params)
