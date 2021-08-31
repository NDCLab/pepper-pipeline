import pathlib
import mne_bids
import json
from mne_bids.config import ALLOWED_DATATYPE_EXTENSIONS

from itertools import product


def load_params(user_param_path):
    with open(user_param_path) as fp:
        user_params = json.load(fp)
        return user_params


def _init_subjects(filter_sub, root, ch_type):
    """Initialize collection of files by loading selected subjects
    Parameters
    ----------
    filter_sub : list
                 a list of subjects to select from all BIDS files
    root : str
           root of BIDS dataset
    ch_type: str
             type of BIDS dataset

    Returns
    ----------
    files: list
           a list of partially filtered BIDS paths according to subjects
    """
    if filter_sub == ["*"]:
        filter_sub = mne_bids.get_entity_vals(root, 'subject')

    filtered_subjects = []
    bids_root = pathlib.Path(root)
    type_exten = ALLOWED_DATATYPE_EXTENSIONS[ch_type]

    for subject in filter_sub:
        bids_path = mne_bids.BIDSPath(subject=subject,
                                      datatype=ch_type,
                                      root=bids_root)

        files = bids_path.match()
        files_eeg = [f for f in files if f.extension.lower() in type_exten]
        filtered_subjects += files_eeg

    return filtered_subjects


def _filter_tasks(filter_tasks, files):
    """Select tasks as defined by user_params
    Parameters
    ----------
    filter_tasks : list
                   list of tasks to run pipeline on
    files : list
            list of BIDS paths filtered according to subjects

    Returns
    ----------
    files: list
           a list of partially filtered BIDS paths according to tasks
    """
    if filter_tasks == ["*"]:
        return files

    return [f for f in files if f.task in filter_tasks]


def _filter_exceptions(subjects, tasks, runs, files, root, ch_type):
    """Remove exceptions as defined by user_params
    Parameters
    ----------
    subjects, tasks, runs : list
                            a list of subjects, tasks, and runs to be
                            cartesian multiplied to get omitted files
    files: list
           list of partially filtered files according to subject and tasks
    root: str
          root of BIDS dataset
    ch_type: str
             type of BIDS dataset

    Returns
    ----------
    files: list
           a list of fully filtered BIDS paths according to exceptions
    """
    # get cartesian product of subjects, tasks, and runs
    exceptions = list(product(subjects, tasks, runs))

    bids_root = pathlib.Path(root)
    type_exten = ALLOWED_DATATYPE_EXTENSIONS[ch_type]
    # turn each exception into a BIDS path
    for i in range(len(exceptions)):
        file = exceptions[i]

        sub = file[0]
        task = file[1]
        run = file[2]

        bids_path = mne_bids.BIDSPath(subject=sub,
                                      task=task,
                                      run=run,
                                      datatype=ch_type,
                                      root=bids_root)
        e_files = bids_path.match()
        e_files_eeg = [f for f in e_files if f.extension.lower() in type_exten]

        exceptions[i] = e_files_eeg[0]

    # remove any file in files that shows up in exceptions and return
    return [f for f in files if f not in exceptions]


def load_files(data_params):
    """ Load subject files and filter according to load_params of user_params
    Parameters
    ----------
    data_params: dict
                 dictionary containing metadata of BIDS dataset and selection
                 of subjects, tasks, and exceptions

    Returns
    ----------
    files: list
           a list of completely filtered BIDS paths
    """
    # get metadata
    root = data_params["root"]
    ch_type = data_params["channel-type"]

    # get selection of subjects & tasks
    subjects_sel = data_params["subjects"]
    tasks_sel = data_params["tasks"]

    # Get selection of exceptions
    exceptions = data_params["exceptions"]
    e_sub = exceptions["subjects"]
    e_tasks = exceptions["tasks"]
    e_runs = exceptions["runs"]

    # initialize files by loading selected subjects
    files = _init_subjects(subjects_sel, root, ch_type)

    # filter tasks
    files = _filter_tasks(tasks_sel, files)

    # filter exceptions
    files = _filter_exceptions(e_sub, e_tasks, e_runs, files, root, ch_type)

    return files
