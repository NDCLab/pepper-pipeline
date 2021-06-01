from scripts.data import load_data
from scripts.data import write_annotate

import scripts.preprocess.preprocess as preproc
from collections import ChainMap

# get user_params and raw
user_params = load_data.load_param("user_params.json")
eeg_obj = load_data.load_raw(
    "CMI/rawdata/",
    "NDARAB793GL3",
    "01",
    "ContrastChangeBlock1",
    "01",
    "eeg"
)

# for each pipeline step in user_params, execute with specified parameters
func_outputs = [None] * len(user_params)
for idx, (func, params) in enumerate(user_params.items()):
    eeg_obj, func_outputs[idx] = getattr(preproc, func)(eeg_obj, **params)

# collect outputs of each step and annotate changes
output = dict(ChainMap(*func_outputs))
write_annotate.read_dict_to_json(output)
