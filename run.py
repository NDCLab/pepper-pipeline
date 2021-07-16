from scripts.data import load, write
from scripts.preprocess import preprocess

from collections import ChainMap

import mne_bids

# load all parameters
user_params = load.load_params("user_params_except.json")

# get preprocessing and data parameters
preprocess_params = user_params["preprocess"]
data_params = user_params["load_data"]

# get root and channel type of data
root = data_params["root"]
ch_type = data_params["channel-type"]

# get set of subjects & tasks to run while omitting existing exceptions
data = load.load_files(data_params)

# for each file in filtered data
for file in data:
    # get attributes and load raw data
    subj, ses, task, run = file.subject, file.session, file.task, file.run
    eeg_obj = mne_bids.read_raw_bids(file)

    outputs = [None] * len(preprocess_params)
    # for each pipeline step in user_params, execute with parameters
    for idx, (func, params) in enumerate(preprocess_params.items()):
        eeg_obj, outputs[idx] = getattr(preprocess, func)(eeg_obj, **params)
        write.write_eeg_data(eeg_obj, func, subj, ses, task, ch_type, root)

    # collect annotations of each step
    output = dict(ChainMap(*outputs))
    write.read_dict_to_json(output)
