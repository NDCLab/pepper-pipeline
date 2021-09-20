from scripts.data import load, write
from scripts.preprocess import preprocess as pre

from collections import ChainMap

import mne_bids

from scripts.constants import \
    CAUGHT_EXCEPTION_SKIP, \
    EXIT_MESSAGE
import sys

# load all parameters
user_params = load.load_params("user_params.json")

# get data and metadata sections
preprocess_params = user_params["preprocess"]
data_params = user_params["load_data"]
write_params = user_params["output_data"]

# get pipeline parameters
ch_type = data_params["channel-type"]
exit_on_error = data_params["exit_on_error"]
rewrite = data_params["overwrite"]
path = write_params["root"]

# get set of subjects & tasks to run while omitting existing exceptions
data = load.load_files(data_params)

# for each file in filtered data
for file in data:
    # load raw data
    eeg_obj = mne_bids.read_raw_bids(file)
    # initialize output list
    outputs = [None] * len(preprocess_params)

    # for each pipeline step in user_params, execute with parameters
    for idx, (func, params) in enumerate(preprocess_params.items()):
        try:
            eeg_obj, outputs[idx] = getattr(pre, func)(eeg_obj, **params)

            # check if this is the final preprocessed eeg object
            final = idx == len(preprocess_params.items()) - 1
            # write object out to file
            write.write_eeg_data(eeg_obj, func, file, ch_type, final, path,
                                 rewrite)
        except (AttributeError, TypeError, ValueError):
            # if an exception was caught, clean up outputs and skip subject
            print(func, CAUGHT_EXCEPTION_SKIP)
            outputs = [result for result in outputs if result is not None]
            # if pipeline should exit on error, do so
            if exit_on_error:
                sys.exit(EXIT_MESSAGE)
            break

    # collect annotations of each step
    outputs.reverse()
    output = dict(ChainMap(*outputs))
    write.write_output_param(output, file, ch_type, path, rewrite)
