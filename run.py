from scripts.data import load_params
from scripts.data import load_raw
from scripts.data import write_annotate

import scripts.preprocess.preprocess as preproc
from collections import ChainMap

# get user_params from user_params.json
user_params = load_params.user_params

# for each pipeline step in user_params, execute with specified parameters
func_outputs = [None] * len(user_params)
eeg_obj = load_raw.raw
for idx, (func, params) in enumerate(user_params.items()):
    eeg_obj, func_outputs[idx] = getattr(preproc, func)(eeg_obj, **params)

# collect outputs of each step and annotate changes
output = dict(ChainMap(*func_outputs))
write_annotate.read_dict_to_json(output)
