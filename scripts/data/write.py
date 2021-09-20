import json
import os
import mne

from scripts.constants import \
    PIPE_NAME, \
    INTERM, \
    FINAL, \
    SKIP_REWRITE_MSG


def write_output_param(dict_array, file, datatype, root, rewrite):
    """Write output parameters of completed pipeline
    Parameters:
    -----------
    dict_array: dict
                Dictionary object containing conjoined outputs
    file:   String
            Name of unprocessed EEG object
    datatype:   String
                Data-type of file
    root:   String
            Path to write to
    rewrite:    Bool
                Boolean value to indicate if file should be overwritten

    Returns:
    ----------
    None | String
        None is returned if file-write is skipped due to overwrite
        String name of file is returned if file is successfully written
    """
    # get file metadata
    subj, ses, task, run = file.subject, file.session, file.task, file.run

    # Creates the directory if it does not exist
    dir_path = '{}/derivatives/{}/{}/sub-{}/ses-{}/{}/'.format(
        root, PIPE_NAME, PIPE_NAME + FINAL, subj, ses, datatype)

    temp = ""
    for sec in dir_path.split("/"):
        temp += sec + "/"
        # checks that the directory path doesn't already exist
        if not os.path.isdir(temp):
            os.mkdir(temp)  # creates the directory path

    file_name = 'output_preproc_sub-{}_ses-{}_task-{}_run-{}_{}.json'.format(
        subj, ses, task, run, datatype)

    if os.path.isfile(dir_path + file_name) and not rewrite:
        print(SKIP_REWRITE_MSG)
        return None
    with open(dir_path + file_name, 'w') as file:
        str = json.dumps(dict_array, indent=4)
        file.seek(0)
        file.write(str)
    return file_name


def write_eeg_data(obj, func, file, datatype, final, root, rewrite):
    """Used to store the modified raw file after each processing step
    Parameters:
    -----------
    obj:    mne.io.Raw | mne.Epochs
            EEG Object generated from pipeline
    func:   String
            name of the function
    file:   String
            Name of unprocessed EEG object
    datatype:   String
                type of data(e.g EEG, MEG, etc )
    final:  boolean
            boolean that determines if eeg object written is the final
    root:   String
            directory from where the data was loaded
    rewrite:    Bool
                Boolean value to indicate if file should be overwritten

    Returns:
    ----------
    None | String
        None is returned if file-write is skipped due to overwrite
        String name of file is returned if file is successfully written
    """
    # get file metadata
    subj, ses, task, run = file.subject, file.session, file.task, file.run

    # determine file extension based on object type
    obj_type = "_epo.fif" if isinstance(obj, mne.Epochs) else ".fif"

    # determine directory child based on feature position
    child_dir = PIPE_NAME + FINAL if final else PIPE_NAME + INTERM

    # Un-standardize function names for close-to-BIDS standard
    func = PIPE_NAME if final else func.replace("_", "")

    # puts together the path to be created
    dir_path = '{}/derivatives/{}/{}/sub-{}/ses-{}/{}/'.format(
        root, PIPE_NAME, child_dir, subj, ses, datatype)

    dir_section = dir_path.split("/")

    # creates the directory path
    temp = ""
    for sec in dir_section:
        temp += sec + "/"
        # checks that the directory path doesn't already exist
        if not os.path.isdir(temp):
            os.mkdir(temp)  # creates the directory path

    # saves the raw file in the directory
    file_name = 'sub-{}_ses-{}_task-{}_run-{}_proc-{}_{}'.format(
        subj, ses, task, run, func, datatype) + obj_type

    # if the file has already been created, and it should not overwrite
    if os.path.isfile(dir_path + file_name) and not rewrite:
        # skip this write by returning none
        print(SKIP_REWRITE_MSG)
        return None
    obj.save(dir_path + file_name, overwrite=rewrite)
    return file_name


def write_template_params(root, write_root, subjects=None, tasks=None,
                          e_subj=None, e_task=None, e_run=None, to_file=None):
    """Function to write out default user_params.json file
    Parameters:
    -----------
    root:   string
            string of path to data root
    subjects:   list | None
                a list of subjects for subject selection. None is default
    tasks:  list | None
            a list of tasks for task selection. None is default
    e_subj, e_task, e_run:  list(s) | None
                            list to compose cartesian product of exceptions
                            None if default
    to_file:    string | None
                path to write user_params to. None if no writing required.

    Returns:
    ----------
    A dictionary of the default user_params
    """
    user_params = {}

    # Create default values of exceptions
    exceptions = {
        "subjects": "" if e_subj is None else e_subj,
        "tasks": "" if e_task is None else e_task,
        "runs": "" if e_run is None else e_run
    }

    # set up default load_data params
    user_params["load_data"] = {
        "root": root,
        "subjects": ["*"] if subjects is None else subjects,
        "tasks": ["*"] if tasks is None else tasks,
        "exceptions": exceptions,
        "channel-type": "eeg",
        "exit_on_error": False,
        "overwrite": True,
        "parallel_runs": False
    }

    # set up default preprocess params
    user_params["preprocess"] = {
        "filter_data": {
            "l_freq": 0.3,
            "h_freq": 40
        },
        "identify_badchans_raw": {
        },
        "ica_raw": {
            "montage": "standard_1020"
        },
        "segment_data": {
            "tmin": -0.2,
            "tmax": 0.5,
            "baseline": None,
            "picks": None,
            "reject_tmin": None,
            "reject_tmax": None,
            "decim": 1,
            "verbose": False,
            "preload": None
        },
        "final_reject_epoch": {
        },
        "interpolate_data": {
            "mode": "accurate",
            "method": None,
            "reset_bads": None
        },
        "reref_raw": {
        }
    }

    # set up postprocess params Pipeline has not yet been implemented!
    user_params["postprocess"] = {}

    # set up write_data params
    user_params["output_data"] = {
        "root": write_root
    }

    if to_file is not None:
        path_to_file = os.path.join(to_file, "user_params.json")
        with open(path_to_file, 'w') as file:
            str = json.dumps(user_params, indent=4)
            file.seek(0)
            file.write(str)

    return user_params
