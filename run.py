from scripts.data import load_params
from scripts.data import load_raw
from scripts.data import write_annotate

import scripts.preprocess.filter
import scripts.preprocess.segment_data
import scripts.preprocess.final_reject_epoch
import scripts.preprocess.interpolate_data
from collections import ChainMap

# loop over the functions
user_params = load_params.user_params
func_outputs = [None] * len(user_params)
eeg_obj = load_raw.raw

for idx, (func, params) in enumerate(user_params.items()):
    eeg_obj, func_outputs[idx] = getattr(scripts.preprocess.func, func)(eeg_obj, **params)

# and collect their outputs
output = dict(ChainMap(*func_outputs))
write_annotate.read_dict_to_json(output)
