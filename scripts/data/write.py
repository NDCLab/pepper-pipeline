import json
import os
import glob
import mne

from scripts.constants import \
    PIPE_NAME, \
    INTERM, \
    FINAL, \
    ALL, \
    OMIT, \
    DEFAULT_LOAD_PARAMS, \
    DEFAULT_REF_PARAMS, \
    DEFAULT_MONT_PARAMS, \
    DEFAULT_FILT_PARAMS, \
    DEFAULT_IDENT_PARAMS, \
    DEFAULT_SEG_PARAMS, \
    DEFAULT_INTERP_PARAMS, \
    PARAM_FILE_NAME, \
    ICA_NAME, \
    FINAL_NAME, \
    REREF_NAME


def write_output_param(dict_array, file, datatype, root):
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
        root, PIPE_NAME, FINAL, subj, ses, datatype)

    temp = ""
    for sec in dir_path.split("/"):
        temp += sec + "/"
        # checks that the directory path doesn't already exist
        if not os.path.isdir(temp):
            os.mkdir(temp)  # creates the directory path

    file_name = 'output_preproc_sub-{}_ses-{}_task-{}_run-{}_{}.json'.format(
        subj, ses, task, run, datatype)

    with open(dir_path + file_name, 'w') as file:
        str = json.dumps(dict_array, indent=4)
        file.seek(0)
        file.write(str)
    return file_name


def is_preprocessed(file, datatype, root, rewrite):
    # get file metadata
    subj, ses, task, run = file.subject, file.session, file.task, file.run

    # Get final path
    dir_path = '{}/derivatives/{}/{}/sub-{}/ses-{}/{}/'.format(
        root, PIPE_NAME, FINAL, subj, ses, datatype) + "*"

    # Get final file name
    file_name = 'sub-{}_ses-{}_task-{}_run-{}_proc-{}_{}'.format(
        subj, ses, task, run, PIPE_NAME, datatype)

    # glob get file
    file_exists = len(glob.glob(dir_path + file_name))

    if file_exists and not rewrite:
        return True
    return False


def write_eeg_data(obj, func, file, datatype, final, root):
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
    child_dir = FINAL if final else INTERM

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

    obj.save(dir_path + file_name)
    return file_name


def write_template_params(root, write_root, subjects=None, tasks=None,
                          e_subj=None, e_task=None, e_run=None, to_file=None):
    """Function to write out default user_params.json file
    Parameters:
    -----------
    root:   string
            string of path to data root
    write_root: string
                string of path to write root
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
        "subjects": OMIT if e_subj is None else e_subj,
        "tasks": OMIT if e_task is None else e_task,
        "runs": OMIT if e_run is None else e_run
    }

    # set up default load_data params
    user_params[type(DEFAULT_LOAD_PARAMS).__name__] = {
        "root": root,
        "subjects": ALL if subjects is None else subjects,
        "tasks": ALL if tasks is None else tasks,
        "exceptions": exceptions,
        "channel_type": DEFAULT_LOAD_PARAMS.channel_type,
        "exit_on_error": DEFAULT_LOAD_PARAMS.exit_on_error,
        "overwrite": DEFAULT_LOAD_PARAMS.overwrite,
        "parallel_runs": DEFAULT_LOAD_PARAMS.parallel_runs
    }

    # set up default preprocess params
    user_params["preprocess"] = {
        type(DEFAULT_REF_PARAMS).__name__:
            DEFAULT_REF_PARAMS._asdict(),
        type(DEFAULT_MONT_PARAMS).__name__:
            DEFAULT_MONT_PARAMS._asdict(),
        type(DEFAULT_FILT_PARAMS).__name__:
            DEFAULT_FILT_PARAMS._asdict(),
        type(DEFAULT_IDENT_PARAMS).__name__:
            DEFAULT_IDENT_PARAMS._asdict(),
        ICA_NAME: {},
        type(DEFAULT_SEG_PARAMS).__name__:
            DEFAULT_SEG_PARAMS._asdict(),
        FINAL_NAME: {},
        type(DEFAULT_INTERP_PARAMS).__name__:
            DEFAULT_INTERP_PARAMS._asdict(),
        REREF_NAME: {}
    }

    # set up write_data params
    user_params["output_data"] = {
        "root": write_root
    }

    if to_file is not None:
        path_to_file = os.path.join(to_file, PARAM_FILE_NAME)
        with open(path_to_file, 'w') as file:
            str = json.dumps(user_params, indent=4)
            file.seek(0)
            file.write(str)

    return user_params
