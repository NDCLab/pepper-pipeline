from scripts.data.load import load_params, load_raw, load_files
from scripts.data.write import read_dict_to_json, write_eeg_data
from scripts.preprocess import preprocess

from collections import ChainMap

# load all parameters
user_params = load_params("user_params.json")

# get preprocessing and data parameters
preprocess_params = user_params["preprocess"]
data_params = user_params["load_data"]

# get root and channel type of data
root = data_params["root"]
ch_type = data_params["channel-type"]

# get set of subjects & tasks to run while omitting existing exceptions
data = load_files(root, ch_type, data_params)

'''
# for each file
for file in data:
    subj, ses, task, run = file.subject, file.session, file.task, file.run
    eeg_obj = load_raw(root, subj, ses, task, run, ch_type)

    outputs = [None] * len(preprocess_params)
    # for each pipeline step in user_params, execute with parameters
    for idx, (func, params) in enumerate(preprocess_params.items()):
        eeg_obj, outputs[idx] = getattr(preprocess, func)(eeg_obj, **params)
        write_eeg_data(eeg_obj, func, subj, ses, task, ch_type, root)

    # collect annotations of each step
    output = dict(ChainMap(*outputs))
    read_dict_to_json(output)
'''