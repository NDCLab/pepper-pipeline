import json
import sys
import os


def read_dict_to_json(dict_array):
    if dict_array is None:
        print("Invalid dictionary array", file=sys.stderr)
        sys.exit(1)

    with open('output_preproc.json', 'w') as file:
        str = json.dumps(dict_array, indent=4)
        file.seek(0)
        file.write(str)


def write_eeg_data(raw, func, subject, session, task, datatype, root):
    """Used to store the modified raw file after each processing step
    Parameters:
    -----------
    raw:    Raw
            Raw data in FIF format
    func:   String
            name of the function
    subject:    String
                name of the subject
    session:    String
                session number
    task:   String
            name of the task
    datatype:   String
                type of data(e.g EEG, MEG, etc )
    root:   String
            directory from where the data was loaded
    """

    # puts together the path to be created
    dir_path = '{}/raw_derivatives/preprocessed/sub-{}/ses-{}/{}/'.format(
        root.split("/")[0], subject, session, datatype)

    dir_section = dir_path.split("/")

    # creates the directory path
    temp = ""
    for sec in dir_section:
        temp += sec + "/"
        # checks that the directory path doesn't already exist
        if not os.path.isdir(temp):
            os.mkdir(temp)  # creates the directory path

    # saves the raw file in the directory
    raw_savePath = dir_path + 'ses-{}_task-{}_{}_{}'.format(
        subject, task, datatype, func)

    raw.save(raw_savePath, overwrite=True)


def write_template_params(root, subjects=None, tasks=None,
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
        "channel-type": "eeg"
    }

    # set up default preprocess params
    user_params["preprocess"] = {
        "filter_data": {
            "l_freq": 0.3,
            "h_freq": 40
        },
        "bad_channels": {
        },
        "ica": {
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
        "rereference_data": {
        }
    }

    # set up postprocess params Pipeline has not yet been implemented!
    user_params["postprocess"] = {}

    # set up write_data params
    user_params["output_data"] = {
        "root": "CMI"
    }

    if to_file is not None:
        path_to_file = os.path.join(to_file, "user_params.json")
        with open(path_to_file, 'w') as file:
            str = json.dumps(user_params, indent=4)
            file.seek(0)
            file.write(str)

    return user_params
