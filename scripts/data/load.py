import pathlib
import mne_bids
import json


def load_subject_files(path, sub, datatype):
    bids_root = pathlib.Path(path)
    bids_path = mne_bids.BIDSPath(subject=sub,
                                  datatype=datatype,
                                  root=bids_root)
    return bids_path.match()


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


def init_data(user_params):
    init_data = user_params["load_data"]
    return init_data["root"], init_data["subjects"], init_data["channel"]
