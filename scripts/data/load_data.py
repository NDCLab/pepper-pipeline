import pathlib
import mne_bids
import json


# load raw data
def load_raw(path, sub, ses, task, run, datatype):
    bids_root = pathlib.Path(path)
    bids_path = mne_bids.BIDSPath(subject=sub,
                                  session=ses,
                                  task=task,
                                  run=run,
                                  datatype=datatype,
                                  root=bids_root)
    return mne_bids.read_raw_bids(bids_path)


def load_param(user_param_path):
    with open(user_param_path) as fp:
        user_params = json.load(fp)
        return user_params
