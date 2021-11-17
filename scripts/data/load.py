import pathlib
import mne_bids
import json

from itertools import product
import os
import warnings
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


def _check_params(s_sub, s_task, e_sub, e_task, e_run):
    if not isinstance(s_sub, list):
        raise TypeError(INVALID_SUBJ_PARAM_MSG)
    if not isinstance(s_task, list):
        raise TypeError(INVALID_TASK_PARAM_MSG)

    if not isinstance(e_sub, list) and e_sub != OMIT:
        raise TypeError(INVALID_E_SUBJ_MSG)
    elif not isinstance(e_task, list) and e_task != OMIT:
        raise TypeError(INVALID_E_TASK_MSG)
    elif not isinstance(e_run, list) and e_run != OMIT:
        raise TypeError(INVALID_E_RUN_MSG)


def _select_except(s_sub, s_task, e_sub, e_task, e_run, root, ch_type):
    """Initialize collection of files by loading selected subjects
    Parameters

    Returns
    """
    # Set warnings to be handled as errors
    warnings.filterwarnings("error")

    bids_root = pathlib.Path(root)
    selected_files = []

    # Select all subjects and tasks if specified
    if s_sub == ALL:
        s_sub = mne_bids.get_entity_vals(bids_root, 'subject')
    if s_task == ALL:
        s_task = mne_bids.get_entity_vals(bids_root, 'task')
    # By default, select all subjects and runs
    ses = mne_bids.get_entity_vals(bids_root, 'session')
    run = mne_bids.get_entity_vals(bids_root, 'run')
    # Get cartesian product of selection
    selections = list(product(s_sub, s_task, ses, run))

    # Select all except sub, tasks, and runs if specified
    if e_sub == ALL:
        e_sub = mne_bids.get_entity_vals(bids_root, 'subject')
    if e_task == ALL:
        e_task = mne_bids.get_entity_vals(bids_root, 'task')
    if e_run == ALL:
        e_run = mne_bids.get_entity_vals(bids_root, 'run')
    # Get cartesian product of exceptions
    exceptions = list(product(e_sub, e_task, ses, e_run))

    # Select files if they exist
    for sub, task, ses, run in tqdm(selections):
        # Skip file if RunTimeWarning
        try:
            bids_path = mne_bids.BIDSPath(subject=sub,
                                          task=task,
                                          session=ses,
                                          run=run,
                                          datatype=ch_type,
                                          extension='.vhdr',
                                          root=bids_root)
            selected_files.append(bids_path)
        except RuntimeWarning:
            continue

    # Remove exception files if they exist
    for sub, task, ses, run in tqdm(exceptions):
        # Skip file if RunTimeWarning
        try:
            bids_path = mne_bids.BIDSPath(subject=sub,
                                          task=task,
                                          session=ses,
                                          run=run,
                                          datatype=ch_type,
                                          extension='.vhdr',
                                          root=bids_root)
            selected_files.remove(bids_path)
        except (RuntimeWarning, ValueError):
            continue

    return selected_files


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

    # Raise exception if any data param violates preconditions
    _check_params(subjects_sel, tasks_sel, e_sub, e_tasks, e_runs)

    # initialize files by loading selected subjects
    paths = _select_except(subjects_sel, tasks_sel, e_sub, e_tasks, e_runs,
                           root, ch_type)

    return paths
