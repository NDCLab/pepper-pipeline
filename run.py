from scripts.data import load, write
from scripts.preprocess import preprocess

from collections import ChainMap

import mne_bids
import sys

# load all parameters
user_params = load.load_params("user_params.json")

# get data and metadata parameters
preprocess_params = user_params["preprocess"]
data_params = user_params["load_data"]
write_params = user_params["output_data"]

# get output root and channel type of data
ch_type = data_params["channel-type"]
output_path = write_params["root"]

# overwrite data_params using sys.argv arguments
if len(sys.argv) > 1:
    data_params["subjects"] = [sys.argv[1]]

# get set of subjects & tasks to run while omitting existing exceptions
data = load.load_files(data_params)

# for each file in filtered data
for file in data:
    # load raw data
    eeg_obj = mne_bids.read_raw_bids(file)

    outputs = [None] * len(preprocess_params)
    # for each pipeline step in user_params, execute with parameters
    for idx, (func, params) in enumerate(preprocess_params.items()):
        eeg_obj, outputs[idx] = getattr(preprocess, func)(eeg_obj, **params)

        # check if this is the fully preprocessed eeg object
        final = idx == len(preprocess_params.items()) - 1
        write.write_eeg_data(eeg_obj, func, file, ch_type, final, output_path)

    # collect annotations of each step
    outputs.reverse()
    output = dict(ChainMap(*outputs))
    write.read_dict_to_json(output, file, ch_type, output_path)
