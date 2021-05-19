from load_params import user_params
from load_data import raw 
import dictCollat as out
import pipeline

from collections import ChainMap

# loop over the functions
func_outputs = [None] * len(user_params)
eeg_obj = raw

for idx, (func, params) in enumerate(user_params.items()):
    eeg_obj, func_outputs[idx] = getattr(pipeline, func)(eeg_obj, **params)

# and collect their outputs
output = dict(ChainMap(*func_outputs))
out.read_dict_to_json(output)
