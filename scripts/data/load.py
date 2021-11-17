import pathlib
import mne_bids
import json
from mne_bids.config import ALLOWED_DATATYPE_EXTENSIONS

from itertools import product
import os
from tqdm import tqdm

from scripts.constants import \
    INVALID_UPARAM_MSG, \
    INVALID_SUBJ_PARAM_MSG, \
    INVALID_TASK_PARAM_MSG, \
    MISSING_PATH_MSG, \
    MISSING_DATA_MSG, \
    INVALID_E_SUBJ_MSG, \
    INVALID_E_TASK_MSG, \
    INVALID_E_RUN_MSG, \
    ALL, \
    OMIT


def load_params(user_param_path):
    try:
        with open(user_param_path) as fp:
            user_params = json.load(fp)
            return user_params
    except FileNotFoundError:
        raise FileNotFoundError(user_param_path, ":", MISSING_PATH_MSG)


def _filter_subjects(select_sub, root, ch_type):
    """Initialize collection of files by loading selected subjects
    Parameters
    ----------
    select_sub : list
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
    if not isinstance(select_sub, list):
        raise TypeError(INVALID_SUBJ_PARAM_MSG)
    if select_sub == ALL:
        select_sub = mne_bids.get_entity_vals(root, 'subject')

    filtered_subjects = []
    bids_root = pathlib.Path(root)
    type_exten = ALLOWED_DATATYPE_EXTENSIONS[ch_type]

    print("Loading participants")
    for subject in tqdm(select_sub):
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
    if not isinstance(filter_tasks, list):
        raise TypeError(INVALID_TASK_PARAM_MSG)
    if filter_tasks == ALL:
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
    if not isinstance(subjects, list) and subjects != OMIT:
        raise TypeError(INVALID_E_SUBJ_MSG)
    elif not isinstance(tasks, list) and tasks != OMIT:
        raise TypeError(INVALID_E_TASK_MSG)
    elif not isinstance(runs, list) and runs != OMIT:
        raise TypeError(INVALID_E_RUN_MSG)

    if subjects == ALL:
        subjects = mne_bids.get_entity_vals(root, 'subject')
    if tasks == ALL:
        tasks = mne_bids.get_entity_vals(root, 'task')
    if runs == ALL:
        runs = mne_bids.get_entity_vals(root, 'run')

    # get cartesian product of subjects, tasks, and runs
    exceptions = list(product(subjects, tasks, runs))

    bids_root = pathlib.Path(root)
    type_exten = ALLOWED_DATATYPE_EXTENSIONS[ch_type]
    # turn each exception into a BIDS path
    print("Filtering exceptions")
    for i in tqdm(range(len(exceptions))):
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

        if len(e_files_eeg):
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
    try:
        root = data_params["root"]
        ch_type = data_params["channel-type"]

        # get selection of subjects & tasks
        subjects_sel = data_params["subjects"]
        tasks_sel = data_params["tasks"]

        # Get selection of exceptions
        exceptions = data_params["exceptions"]
    except TypeError:
        raise TypeError(INVALID_UPARAM_MSG)

    # if the path does not exist, exit and throw exception
    if not os.path.exists(root):
        raise FileNotFoundError(root, ":", MISSING_PATH_MSG)
    # if data does not exist at bottom-most path, exit and throw exception
    for _, dirnames, filenames in os.walk(root):
        if not dirnames:
            if not len(filenames):
                raise FileNotFoundError(root, ":", MISSING_DATA_MSG)

    e_sub = exceptions["subjects"]
    e_tasks = exceptions["tasks"]
    e_runs = exceptions["runs"]

    # initialize files by loading selected subjects
    files = _filter_subjects(subjects_sel, root, ch_type)
    # filter tasks
    files = _filter_tasks(tasks_sel, files)
    # filter exceptions
    files = _filter_exceptions(e_sub, e_tasks, e_runs, files, root, ch_type)

    return files
